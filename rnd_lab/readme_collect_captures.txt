Packet capture:

In the directory where the file collect_capture.py is saved.
Run command:
python collect_capture.py with four command line arguments.

where:
interface= The interface on which you want to capture trace
exec_time= For how long you want to capture
host_user= Username of your host machine on which you want to save the capture
dest_directory= The path on you machine where you want to save the capture

For example:

python collect_capture.py eth1 10 vm1 /home/vm1/trace

where: 
  eth1 indicates the interface on which we want to capture the trace 
  10 indicated the time for which we want to capture the trace
  vm1 indicates the username of the host machine provided  by the Proffesor 
  /home/vm1/trace indicates the directory on my machine where we want to save my capture
  
  After running this command you will be prompted to enter the host password for two times.
  After completion of command you will find pcap file in the host machine in the directory you specified. 
  The file will be saved in the format 
  filename=myhost+"_"+interface+"_"+timestamp+".pcap"

  
