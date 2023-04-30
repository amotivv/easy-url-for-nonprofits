import os
import base64

# Generate a random 32-byte JWT secret key
secret_key = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')

# Load the existing environment variables from the .env file
env_vars = {}
if os.path.exists('.env'):
    with open('.env', 'r') as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            env_vars[key] = value

# Update the JWT_SECRET_KEY variable
env_vars['JWT_SECRET_KEY'] = secret_key

# Save the updated environment variables to the .env file
with open('.env', 'w') as file:
    for key, value in env_vars.items():
        file.write(f'{key}={value}\n')

print(f'Generated JWT secret key: {secret_key}')
