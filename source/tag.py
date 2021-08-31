import boto3
from botocore.exceptions import ClientError


# This script can be used to tag ECS Tasks with Name = Service name which have not used the propergate at creation setting
# In the bu_usage_view.sql line 49 resource_tags_aws_ecs_service_name can be changed too resource_tags_user_name and this.
def main():
    client = boto3.client('ecs', region_name = "us-east-2")
    
    #List all clusters
    
    clusters = client.list_clusters()

    for cluster_arn in clusters['clusterArns']:

        clusters_info = client.describe_clusters(
            clusters = [cluster_arn]
        )
        print(cluster_arn)

        # cluster_name= clusters_info['clusters'][0].get('clusterName')
        # #clusters_info.

        try: 
            #Get Services in a cluster
            services = client.list_services(
                cluster=cluster_arn,
                launchType='EC2'
            )
            #
            for service_arn in services['serviceArns']:

                service_info = client.describe_services(
                    cluster=cluster_arn,
                    services=[service_arn],
                )
                service_name= service_info['services'][0].get('serviceName')

                #List Tasks in the service
                tasks = client.list_tasks(
                    cluster=cluster_arn,
                    serviceName=service_name,
                    launchType='EC2'
                )

                
               
                #Check Task Tags 
                for task_arn in tasks['taskArns']:
                    task_tags = client.list_tags_for_resource(
                    resourceArn=task_arn
                    )  
                    #import pdb; pdb.set_trace()
                   
                    if [x['key'] for x in task_tags['tags']  if 'aws:ecs:serviceName' in x['key']] or [x['key'] for x in task_tags['tags']  if 'Name' in x['key']] :     
                        print(f"{task_arn} is tagged")
                    else:

                        #Tag Task if not already tagged with Name
                        response = client.tag_resource(
                            resourceArn=task_arn,
                            tags=[
                                {
                                    'key': 'Name',
                                    'value': service_name
                                },
                            ]
                        )
                        print(f"{task_arn} now tagged with Name:{service_name}")
        except ClientError as e:
            print(e)
            pass
main()
