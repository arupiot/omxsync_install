try:
    from config_local import (
                              HOSTNAME,
                              USERNAME,
                              PASSWORD,
                              ACCESS_IP,
                              )

except Exception as e:
    print("ERROR: you have to add a file called config_local.py next to this file with the above values")
