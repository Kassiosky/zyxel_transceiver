import asyncio
import os
import telnetlib3
import re
import json
from datetime import datetime
from dotenv import load_dotenv


async def telnet_command(host, username, password, command, retries=10, delay=10):
    """Conecta via Telnet, faz login, executa um comando e retorna a saída completa."""
    print(f'Connecting into {host}...')

    attempt = 0
    while attempt < retries:
        try:
            # Open a Telnet connection
            reader, writer = await telnetlib3.open_connection(host, port=23, encoding='utf-8')
            print(f"Connedted [{host}]")

            await reader.readuntil(b"User name:")
            writer.write(username + "\n")
            await writer.drain()

            await reader.readuntil(b"Password:")
            writer.write(password + "\n")
            await writer.drain()
            print("Logged.")

            await asyncio.sleep(5)
            initial_output = await reader.read(2048)

            match = re.search(r"[\r\n]([^\r\n#>]+)[#>]", initial_output)
            prompt = match.group(1).strip() if match else "#"
            print(f"SW Hostname: {prompt}")

            writer.write(command + "\n")
            await writer.drain()

            await asyncio.sleep(4)

            output = ""
            while True:
                chunk = await reader.read(2048)
                if not chunk:
                    break
                output += chunk
                if f"{prompt}#" in output or f"{prompt}>" in output:
                    break

            writer.write("exit\n")
            await writer.drain()

            output_clean = re.sub(rf"^{re.escape(command)}\s*", "", output.strip())

            # Process the extracted data using regex
            data_pattern = re.compile(r"([A-Za-z\s\(\)]+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)")
            data = {}

            for match in data_pattern.finditer(output_clean):
                label = match.group(1).strip()
                values = {
                    "Current": match.group(2),
                    "High Alarm": match.group(3),
                    "High Warn": match.group(4),
                    "Low Warn": match.group(5),
                    "Low Alarm": match.group(6)
                }
                data[label] = values

            tx_bias_pattern = re.compile(r"TX Bias\(mA\)\s*([+\-]?\d+\.\d+)\s*([+\-]?\d+\.\d+)\s*([+\-]?\d+\.\d+)\s*([+\-]?\d+\.\d+)\s*([+\-]?\d+\.\d+)")
            tx_bias_match = tx_bias_pattern.search(output_clean)
            if tx_bias_match:
                data["TX Bias(mA)"] = {
                    "Current": tx_bias_match.group(1),
                    "High Alarm": tx_bias_match.group(2),
                    "High Warn": tx_bias_match.group(3),
                    "Low Warn": tx_bias_match.group(4),
                    "Low Alarm": tx_bias_match.group(5)
                }

            # Prepare the final log data
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_data = {
                "device_name": prompt,
                "date": current_time,
                "transceiver_data": data
            }

            return json.dumps(log_data, indent=4)

        except Exception as e:
            print(f'Err: {e}, Trying again {attempt + 1}/{retries}')
            attempt += 1
            await asyncio.sleep(delay)

    return None


async def main(HOST, USERNAME, PASSWORD, PORT):
    ## Port it the port that you wanna see the  transceiver information
    COMMAND = f"show interfaces transceiver {PORT}"
    output = await telnet_command(HOST, USERNAME, PASSWORD, COMMAND)

    if output:
        print("Data extracted in JSON:")
        print(output)
    else:
        print("Failed to read data")


# Run the function with the correct variable names
asyncio.run(main(HOST="127.0.0.1", USERNAME="admin", PASSWORD="PASSWORD%", PORT="21"))
