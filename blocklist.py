"""BlockList.py

This file just contains the blocklist of the JWT token. It will be imported by 
app and the logout resource so the token can be added to the blocklist wh the 
user logs out
"""
BLOCKLIST = set()
