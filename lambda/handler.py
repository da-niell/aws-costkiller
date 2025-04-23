import boto3
import json
from datetime import datetime
import os

s3 = boto3.client('s3')
BUCKET_NAME = os.getenv('REPORT_BUCKET', 'costkiller-reports')


def detect_unused_ec2():
    ec2 = boto3.client('ec2')
    stopped_instances = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
    )

    unused = []
    for reservation in stopped_instances['Reservations']:
        for instance in reservation['Instances']:
            unused.append({
                'id': instance['InstanceId'],
                'type': 'EC2',
                'reason': 'Instance is stopped',
                'estimated_monthly_cost_usd': 10  # Aproximado
            })
    return unused

def detect_unused_ebs():
    ec2 = boto3.client('ec2')
    volumes = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )

    unused = []
    for volume in volumes['Volumes']:
        unused.append({
            'id': volume['VolumeId'],
            'type': 'EBS',
            'reason': 'Volume not attached',
            'estimated_monthly_cost_usd': round(volume['Size'] * 0.10, 2)  # $0.10/GB
        })
    return unused

def detect_empty_s3():
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    unused = []
    for bucket in response['Buckets']:
        name = bucket['Name']
        try:
            objs = s3.list_objects_v2(Bucket=name, MaxKeys=1)
            if objs['KeyCount'] == 0:
                unused.append({
                    'id': name,
                    'type': 'S3',
                    'reason': 'Bucket is empty',
                    'estimated_monthly_cost_usd': 0.01  # Asumido
                })
        except Exception as e:
            print(f"Error accediendo a {name}: {e}")
    return unused

def lambda_handler(event, context):
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'unused_resources': []
    }

    report['unused_resources'] += detect_unused_ec2()
    report['unused_resources'] += detect_unused_ebs()
    report['unused_resources'] += detect_empty_s3()

    # Nombre de archivo basado en fecha
    filename = f"costkiller-report-{datetime.utcnow().strftime('%Y-%m-%d')}.json"
    body = json.dumps(report, indent=2)

    # Subida a S3
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f"reports/{filename}",
        Body=body,
        ContentType="application/json"
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Report saved to S3', 'file': filename})
    }
