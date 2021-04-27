import socket
import os
import argparse

''' variables '''
#targetfile = None
#rtsp_urlfile = None
targets = None
rtsp_urls = None
screenshot_output_dir = None
unauth_streams = []
screenshot = False
creds = [('root','pass'), ('admin', 'admin'), ('admin', '123456'), ('Admin', '123456'), ('admin', '12345'), ('admin','9999'), ('root', 'root'), ('admin', '4321'), ('admin', '1111111'), ('admin', 'password')]
try_passwords = False
''' Definitions '''
def read_file(file_in):
        file = open(file_in, 'r')
        lines = file.readlines()
        file.close()
        return list(map(str.strip, lines))

''' Arg reader '''
def read_args():
        parser = argparse.ArgumentParser(description='RTSPeep: Test and optionally screenshot anonymous access to RTSP streams')
        parser.add_argument('--targets',  type=str, help='targets (format is one target per line in a plaintext file)', required=True)
        parser.add_argument('--uris', help='Path to RTSP URIs to test')
        parser.add_argument('--screenshot', action='store_true', help='use the --screenshot flag to capture a picture of the anonymously accessible RTSP streams')
        parser.add_argument('--screenshot_outputdir', help='directory to save screenshots of RTSP streams')
        parser.add_argument('--try_passwords', action='store_true', help='test commonly used default passwords against targets where streams are discovered')
        args = parser.parse_args()
        #print(str(args))
        return vars(args)                                                                                                                                                                                                                  
                                                                                                                                                                                                                                           
# might not even need this function                                                                                                                                                                                                        
def safe_attrcheck(dictobj, attr):                                                                                                                                                                                                         
        try:                                                                                                                                                                                                                               
                if attr in dictobj:                                                                                                                                                                                                        
                        return True                                                                                                                                                                                                        
                return False                                                                                                                                                                                                               
        except KeyError as e:                                                                                                                                                                                                              
                return False                                                                                                                                                                                                               
                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                           
def read_files_from_args(args_in):                                                                                                                                                                                                         
        #print(str(args_in['targets']))                                                                                                                                                                                                    
        if not os.path.exists(str(args_in['targets'])):                                                                                                                                                                                    
                print("Target file does not exist. exiting.")                                                                                                                                                                              
                exit(1)                                                                                                                                                                                                                    
        targetfile = args_in['targets']                                                                                                                                                                                                    
        global targets                                                                                                                                                                                                                     
        targets = read_file(targetfile)                                                                                                                                                                                                    
        global rtsp_urls                                                                                                                                                                                                                   
        if safe_attrcheck(args_in, 'uris'):                                                                                                                                                                                                
                if not os.path.exists(str(args_in['uris'])):                                                                                                                                                                               
                        print("URI file does not exist. Using default (generic) RTSP resource '/'")                                                                                                                                        
                        rtsp_urls = ['/']                                                                                                                                                                                                  
                else:                                                                                                                                                                                                                      
                        print(str(args_in['uris']))
                        rtsp_urlfile = args_in['uris']
                        rtsp_urls = read_file(rtsp_urlfile)
        else:
                rtsp_urls = ["/"]
        if safe_attrcheck(args_in, 'try_passwords'):
                global try_passwords
                try_passwords = args_in['try_passwords']
        if safe_attrcheck(args_in, 'screenshot'):
                #print(str(type(args_in['screenshot'])))
                global screenshot
                screenshot = args_in['screenshot']
                if screenshot and safe_attrcheck(args_in, 'screenshot_outputdir'):
                        if not os.path.exists(str(args_in['screenshot_outputdir'])):
                                print("Path to output directory does not exist. exiting.")
                                exit(1)
                        global screenshot_output_dir
                        screenshot_output_dir = args_in['screenshot_outputdir']
                else:
                        if screenshot:
                            print("screenshot output directory is a required argument if --screenshot is used. exiting.")
                            exit(1)

read_files_from_args(read_args())

unauth_streams = []
count = 0
tot_targets = len(targets)
uris_to_test = len(rtsp_urls)
port = 554


def send_describe_request(host, port, username, password, resource):
        global count
        try:
                MAX_PACKET = 32768
                # send DESCRIBE to each target
                u = ''
                if username:
                        u = 'rtsp://' + str(username) + ':' + str(password) + '@' + str(host) + ':' + str(port) + str(resource)
                else:
                        u = 'rtsp://' + str(host) + ':' + str(port) + str(resource)
                print("[ ] targeting host "+str(count)+ " of " + str(tot_targets) + " |" + str(t) + "|  trying RTSP URL " + str(u))
                req = "DESCRIBE "+ str(u) +" RTSP/1.0\r\nCSeq: 2\r\n\r\n"
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((t, 554))
                s.sendall(req.encode())
                data = str(s.recv(MAX_PACKET))
                #print(str(data))
                if "RTSP/1.0 401" in data:
                        print("[-] UNAUTHORIZED or required authentication")
                        return ('401', '')
                elif "RTSP/1.0 400 Bad Request" in data:
                        print("[-] Stream was unauthorized or maybe stream endpoint wrong?")
                        return ('400', '')
                elif "RTSP/1.0 404 Not Found" in data or "RTSP/1.0 404 Stream Not Found" in data:
                        print("[-] Stream was not found. maybe wrong endpoint?")
                        return ('404', '')
                elif "RTSP/1.0 200 OK" in data:
                        print("[+] Available stream found!")
                        return ('200', str(u))
                else:
                        print("[-] unknown response: " + data)
                        return ('UNKN', '')
        except socket.timeout:
                print("there was a timeout while connecting to " + t)
                return ('CONERR', '')
        except socket.error:
                print("there was an error while connecting to " + t)
                return ('CONERR', '')
        except Exception as e:
                print("other exception caught:" + str(e))
                return ('OTHERR', '')

for t in targets:
        count+=1
        print("target: "+ str(count) +" of "+ str(tot_targets) +" |" + str(t) + "|")
        urindex = 0
        for u in rtsp_urls:
                result = send_describe_request(t, port, None, None, u)
                if result[0] == '200':
                        unauth_streams.append((str(t),str(result[1])))
                        break
                elif result[0] == 'CONERR' or result[0] == 'OTHERR' or result[0] == '400' or result[0] == 'UNKN':
                        break
                elif result[0] == '401':
                        # found endpoint but it requires auth
                        if not try_passwords:
                                break
                        flag = False
                        for c in creds:
                                authres = send_describe_request(t, port, c[0], c[1], u)
                                if authres[0] == '200':
                                        print("[+] SUCCESS ----- FOUND DEFAULT CREDENTIALS!")
                                        unauth_streams.append((str(t), str(authres[1])))
                                        flag = True
                                        break
                        if flag:
                                break


print("found " + str(len(unauth_streams)) + " unauthenticated streams!")
print("writing to ./unauth_streams.txt")
try:
        f = open('./unauth_streams.txt','w+')
        for streams in unauth_streams:
                f.write("%s\n" % streams)
        f.close()
except Exception as e:
        print("caught exception when writing output file: " + str(e))

if screenshot:
        import cv2
        def get_screenshot(streamUri,streamID):
                try:
                        cap = cv2.VideoCapture(streamUri)
                        ret, frame = cap.read()
                        cv2.imwrite(screenshot_output_dir + "target_" + str(streamID) + ".png",frame)
                        cap.release()
                except Exception as e:
                        print("error: exception thrown in get_screenshot - " + str(e))
        print("Screenshotting streams... please wait.")
        count = 0
        tot_unauth_streams = len(unauth_streams)
        for streams in unauth_streams:
                count += 1
                print("screenshotting stream " + str(count) + " of " + str(tot_unauth_streams))
                print("target: " + str(streams[1]))
                get_screenshot(streams[1], streams[0])
