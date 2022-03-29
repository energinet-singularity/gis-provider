import os
import pwd

print("Hello {} - welcome to my template-world!".format(pwd.getpwuid(os.getuid())[0]))
