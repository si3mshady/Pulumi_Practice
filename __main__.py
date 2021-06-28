"""An AWS Python Pulumi program"""

# import pulumi
import pulumi_aws as aws

def vpc_init():
    vpc_dev = aws.ec2.Vpc("si3mshady_vpc", cidr_block="10.0.0.0/16", \
        enable_dns_hostnames=True, enable_dns_support=True)

    public_subnet = aws.ec2.Subnet("si3mshady_public_dev_subnet", \
        vpc_id=vpc_dev.id ,cidr_block="10.0.0.0/24",map_public_ip_on_launch=True, \
            tags={"Name": "public_dev_subnet" })

    private_subnet = aws.ec2.Subnet("si3mshady_private_dev_subnet", \
        vpc_id=vpc_dev.id ,cidr_block="10.0.1.0/24",
        tags={"Name": "public_dev_subnet" })

    return vpc_dev, public_subnet, private_subnet

def init_elb():
    elb = aws.elb.LoadBalancer("si3msahdy-elb", availability_zones=["us-east-1b","us-east-1c"], 
     listeners=[
        aws.elb.LoadBalancerListenerArgs(
            instance_port=80,
            instance_protocol="http",
            lb_port=80,
            lb_protocol="http"  
        )])
    return elb

def init_asg_attachment(asg,aws_elb):
    asg_attachment_bar = aws.autoscaling.Attachment("elb_attachment",
        autoscaling_group_name=asg,
        elb=aws_elb.id)
    return asg_attachment_bar

def asg_init(ec2_lt):
    # dev_asg_lt = aws.ec2.LaunchTemplate("dev_asg_lt", name_prefix="dev",
    # image_id="ami-0747bdcabd34c712a", instance_type="t2.micro")
  

    dev_asg_group = aws.autoscaling.Group("dev_asg_group",
    availability_zones=["us-east-1b","us-east-1c"],
    desired_capacity=1,max_size=1, min_size=1,
    launch_template=aws.autoscaling.GroupLaunchTemplateArgs(
    id=ec2_lt.id, version="$Latest"))
    return dev_asg_group

def init_ec2_LaunchTemplate():
    ec2_lt = aws.ec2.LaunchTemplate("si3mshady-ec2-LT", 
    key_name="dragon",image_id="ami-0747bdcabd34c712a",
    tags={
        "Name": "Si3mshady-Pulumi-Deployment",
    },
    vpc_security_group_ids=["sg-035ace78c00a8e1c5"],
    instance_type='t2.micro' )
    return ec2_lt

vpc_dev, public_subnet, private_subnet = vpc_init()
ec2_lt = init_ec2_LaunchTemplate() #generate launch template
dev_asg_group =  asg_init(ec2_lt) #provide lT to ASG
elb = init_elb()
init_asg_attachment(dev_asg_group,elb) #associate elb with asg