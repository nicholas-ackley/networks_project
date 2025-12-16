## Terminal Chat: Terminal-Based LAN Chat Application

Simple client-server chat project, written in Python using sockets and TCP.


# Requirements

In order to run the project, you'll need Python 3.11.0 or greater, which can be found at: https://www.python.org/downloads/windows/ (for Windows) or https://www.python.org/downloads/macos/ (for Mac)

Once downloaded and installed, or in case you already have it, proceed to next section: **Running the project**.


# Running the project

This project is comprised of two files: "server.py" and "client.py". To run the project, you will need to first open a terminal in your OS or in VSCode, and start the server to connect to and route data:

- Running server:

> python server.py

Once the server is active, it will listen for any devices connecting from the same local area network (Host: 0.0.0.0)

Next, you must start the client. This can be done on a terminal running on the same machine as the server, or on a separate device entirely. The clients MUST be connected over the same network as the server machine. Prior to starting the client however, you must change the listed IP address within client.py to be that of the server's LAN address. You can find this info by using ipconfig (Windows):

- Determining host address:

> ipconfig
...
IPv4 Address. . . . . . . . . . . : 192.168.x.xx

- Changing client.py address:

- HOST = "10.169.173.232" --> "<your host address>"

You can then run the client on however many machines you wish. For the purposes of this project, there must be at least 2 clients in order to see messages being broadcasted and sent to specific users.

- Running client:

> python client.py

Within the client, you can broadcast messages to all users by simply typing text without specifying a recipient. For private messages, you include the /pm command, the recipient's username, a space, and the message text.

- Public messaging:

Format: <username> <msg text>
Example: Josh> Hi!

- Private messaging:

Format: /pm <receiver's username> <msg text>
Example: /pm John Hello!

This client supports file sharing functionality as well. With this, users are able to send files to each other by using the /sendfile command, specifying the recipient, and the file path or file name. The server will forward the file header to the recipient, which then automatically saves the incoming file to a folder named "received_files".

- Sending files:

Format: <receiver's username> <file path>
Example: /sendfile John test.txt

To exit out of client.py and disconnect from the chat, use the /quit command.

- Exiting:

> /quit

Use /help to view all commands, including:

/help       Shows help
/clear      Clears history
/time       toggle timestamps
/nick NAME  change name
/sendfile <user> <path>
/pm <user> <message>
/quit       Quit