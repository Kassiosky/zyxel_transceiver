import asyncio
import os
import telnetlib3
import re
import json
from datetime import datetime
from dotenv import load_dotenv
import hashlib
from includes.Logger import Logger


load_dotenv("includes/.env")
log = Logger("telnet")

def hash_ip(ip_address: str) -> str:
    """Generate a SHA-256 hash from an IP address."""
    hash_object = hashlib.sha256(ip_address.encode())  # Encode IP and hash it
    return hash_object.hexdigest()

async def telnet_command(host, username, password, command, retries=5, delay=10):
    """Connect via Telnet, login, execute a command and return the complete output."""
    log.write_log(f'Connecting to {host}...', "debug")
    hash = hash_ip(ip_address=host)
    attempt = 0
    data = {}
    while attempt < retries:
        try:
            reader, writer = await telnetlib3.open_connection(host, port=23, encoding='utf-8')
            log.write_log(f'[{hash}] - Connected to [{host}]', "debug")

            # Login
            await reader.readuntil(b"User name:")
            writer.write(username + "\n")
            await writer.drain()

            await reader.readuntil(b"Password:")
            writer.write(password + "\n")
            await writer.drain()
            log.write_log(f'[{hash}] - Authenticated on [{host}]', "debug")

            # Wait for the prompt
            await asyncio.sleep(5)
            initial_output = await reader.read(2048)

            # Identify the prompt
            match = re.search(r"[\r\n]([^\r\n#>]+)[#>]", initial_output)
            prompt = match.group(1).strip() if match else "#"
            log.write_log(f'[{hash}] - {host} - [{prompt}]', "debug")

            # Send the command
            writer.write(command + "\n")
            await writer.drain()

            # Wait to ensure the response is received
            await asyncio.sleep(4)

            # Read the output until the next prompt
            output = ""
            while True:
                chunk = await reader.read(2048)
                if not chunk:
                    break
                output += chunk
                if f"{prompt}#" in output or f"{prompt}>" in output:
                    break

            # Exit the Telnet session
            writer.write("exit\n")
            await writer.drain()
            log.write_log(f'[{hash}] - {host} Exiting Telnet session.', "debug")

            # Clean the output and extract the relevant data
            output_clean = re.sub(rf"^{re.escape(command)}\s*", "", output.strip())

            # Regex to capture transceiver data
            data_pattern = re.compile(
                r"([A-Za-z\s\(\)]+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)"
            )

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

            # Adjust for TX Bias(mA) using regex
            tx_bias_pattern = re.compile(
                r"TX Bias\(mA\)\s*([+\-]?\d+\.\d+)\s*([+\-]?\d+\.\d+)\s*([+\-]?\d+\.\d+)\s*([+\-]?\d+\.\d+)\s*([+\-]?\d+\.\d+)"
            )
            tx_bias_match = tx_bias_pattern.search(output_clean)
            if tx_bias_match:
                data["TX Bias(mA)"] = {
                    "Current": tx_bias_match.group(1),
                    "High Alarm": tx_bias_match.group(2),
                    "High Warn": tx_bias_match.group(3),
                    "Low Warn": tx_bias_match.group(4),
                    "Low Alarm": tx_bias_match.group(5)
                }

            # Add current date and device name
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_data = {
                "device_name": prompt,
                "date": current_time,
                "transceiver_data": data,
                "status_code":200
            }


            return json.dumps(log_data, indent=4)

        except Exception as e:
            print(f'Erro: {e}, tentativa {attempt + 1}/{retries}')
            attempt += 1
            await asyncio.sleep(delay)

    # If we reach here, all attempts have been exhausted:
    error_response = {
        "message": "Cannot connect to host",
        "status_code": 500
    }
    log.write_log(f"All {retries} connection attempts failed for host {host}", "error")

    return json.dumps(error_response, indent=4)


# Função principal
async def main():
    HOST = os.getenv('switch_list')
    USERNAME = os.getenv('default_switch_user')
    PASSWORD = os.getenv('default_switch_password')
    COMMAND = os.getenv('switch_command')

    output = await telnet_command(HOST, USERNAME, PASSWORD, COMMAND)
    log.write_log(f"Received data from {HOST}: {output}", "debug")

    with open("logs/log_transceiver_data.json", "w") as json_file:
        json.dump(json.loads(output), json_file, indent=4)
