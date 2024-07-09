import hashlib
import base64

def verify_password(stored_password, provided_password):
    algorithm, iterations, salt, stored_hash = stored_password.split('$')
    iterations = int(iterations)
    salt = salt.encode('utf-8')
    stored_hash = base64.b64decode(stored_hash)
    
    # Hash the provided password using the same parameters
    new_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, iterations)
    
    # Compare the new hash with the stored hash
    return new_hash == stored_hash

# Example usage
stored_password = "pbkdf2_sha256$720000$zeZJJK6cAZLvqwEeLwkq6o$Uz8yE8Ua8nbsO5CHtFDPhHCEnESDG0j87I31rEDwt7Y="
provided_password = "password123"  # The password to check

if verify_password(stored_password, provided_password):
    print("Password is correct")
else:
    print("Password is incorrect")