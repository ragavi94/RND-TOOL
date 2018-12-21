The input/output json conisists of two main objects : "Device" and "Link" . The topology itself can have multiple devices and links and hence they are treated as list of objects.

Below is how an input json would look like: (found in /etc/rnd_lab folder). The input json can also be used to update the topology (add/delete/modify properties) at a later stage.

{
    "topology": [
        {
	    "topology id": "",
	    "topology type": "",
            "link": [
                { 
			//Link information goes here
		}
		],
	    "device": [
		{
			//Device information goes here
		}
		],
	}
	]
}

The output json is created once the topology gets created on running the ansible playbook and can be found in the /var/lib/rnd_lab folder and is of the similar structure as above but with additional objects like "created_time" , "modified_time" , "device_status" etc




