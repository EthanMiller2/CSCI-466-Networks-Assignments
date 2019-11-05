# import http.server
# import SimpleHTTPServer
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import socketserver
import sys
import time

cNum = 4
bNum = 4
rNum = 3
sNum = 3
dNum = 2
class MyTCPServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        try:
            params = dict([p.split('=') for p in parsed_path[4].split('&')])
        except:
            params = {}

        global cNum
        global bNum
        global rNum
        global sNum
        global dNum

        user_message = ""
        try:
            x_coordinate = params["x_coordinate"]
            y_coordinate = params["y_coordinate"]

            x_coordinate = int(x_coordinate)
            y_coordinate = int(y_coordinate)

            if (x_coordinate > 9 or x_coordinate < 0) or (y_coordinate > 9 or y_coordinate < 0):
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                user_message = "MISS, Fired off of board"
                self.wfile.write(bytes(user_message, "UTF-8"))

            else:
                fireCoordinates = own_board[x_coordinate][y_coordinate]
                if (fireCoordinates == 'X'):
                    user_message = "Coordinate has already been fired on"
                    print_board(own_board)
                    self.send_response(410)
                    self.send_header('Content-type', 'text/hmtl')
                    self.end_headers()
                    self.wfile.write(bytes("Coordinate has already been fired on and was a hit", "UTF-8"))
                elif(fireCoordinates == '0'):
                    user_message = "Coordinate has already been fired on"
                    print_board(own_board)
                    self.send_response(410)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(bytes("Coordinate has already been fired on and was a miss", "UTF-8"))
                elif(fireCoordinates == '_'):
                    user_message = "HIT=0"
                    own_board[x_coordinate][y_coordinate] = "0"
                    print_board(own_board)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(bytes(user_message, "UTF-8"))
                else:
                    user_message = "HIT=1"
                    own_board[x_coordinate][y_coordinate] = "X"
                    print_board(own_board)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    if fireCoordinates == 'C':
                        cNum = cNum - 1
                        if cNum == 0:
                            user_message = user_message + "\&SINK=C"
                    elif fireCoordinates == 'B':
                        bNum = bNum - 1
                        if bNum == 0:
                            user_message = user_message + "\&SINK=B"
                    elif fireCoordinates == 'R':
                        rNum = rNum - 1
                        if rNum == 0:
                            user_message = user_message + "\&SINK=R"
                    elif fireCoordinates == 'S':
                        sNum = sNum - 1
                        if sNum == 0:
                            user_message = user_message + "\&SINK=S"
                    elif fireCoordinates == 'D':
                        dNum = dNum - 1
                        if dNum == 0:
                            user_message = user_message + "\&SINK=D"

                    self.wfile.write(bytes(user_message, "UTF-8"))

        except:
            user_message = "Invalid request"
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()


        print(user_message)

    if cNum == 0 and bNum == 0 and rNum == 0 and sNum == 0 and dNum == 0:
        print("Congrats you sunk all ships!")
        sys.exit()


def print_board(board):
    for row in board:
        print('  '.join(row))

def read_file(board_file):
    with open(board_file) as board_file:
        content = [list(line) for line in board_file]
    return content

def run(server_class = HTTPServer, handler_class = MyTCPServer):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print(time.asctime(), "Server Starts - %s:%s" % ('', port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
        httpd.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % ('', port))

if __name__ == "__main__":
    port = int(sys.argv[1])
    input_file = str(str(sys.argv[2]))
    own_board = read_file(input_file)
    opp_board = read_file('opp_board.txt')
    print("Own board")
    print_board(own_board)
    print("------------")
    print("Opp board")
    print_board(opp_board)
    print ("serving at port", port)
    run()