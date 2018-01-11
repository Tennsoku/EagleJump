import boto.ec2

con = boto.ec2.connect_to_region("us-east-1",aws_access_key_id='...',aws_secret_access_key='...')
instance="i-0ba81d58db540f046"

def get_instance_status(conn, instance_ids=None):

	instances = conn.get_all_instance_status(instance_ids=instance_ids)
	print instances

	if not instances:
		return "none"
	else:
		return instances[0].system_status.status

while (get_instance_status(con, instance_ids=instance) == 'ok'):
	print get_instance_status(conn, instance_ids=instance.id)
	time.sleep(1)

print "down"
