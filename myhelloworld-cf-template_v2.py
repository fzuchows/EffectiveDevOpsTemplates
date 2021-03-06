"""Generating CloudFormation template."""

from ipaddress import ip_network
from ipify import get_ip
from troposphere import (
  Base64,
  ec2,
  GetAtt,
  Join,
  Output,
  Parameter,
  Ref,
  Template,
)

ApplicationPort = "3000"
PublicCidrIp = str(ip_network(get_ip()))

t = Template()

t.add_description("Effective DevOps in AWS: HelloWorld web app")

t.add_parameter(Parameter(
  "KeyPair",
  Description="Name of an existing KeyPair to SSH",
  Type="AWS::EC2::KeyPair::KeyName",
  ConstraintDescription="must be the name of an existing EC2 KeyPair.",
))

t.add_resource(ec2.SecurityGroup(
  "SecurityGroup",
  GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
  SecurityGroupIngress=[
    ec2.SecurityGroupRule(
      IpProtocol="tcp",
      FromPort="22",
      ToPort="22",
      CidrIp=PublicCidrIp,
    ),
    ec2.SecurityGroupRule(
      IpProtocol="tcp",
      FromPort=ApplicationPort,
      ToPort=ApplicationPort,
      CidrIp="0.0.0.0/0",
    ),
  ],   
))

ud=Base64(Join('\n', [
  "#!/bin/bash",
  "sudo yum install -y gcc-c++ make wget",
  "curl -sL https://rpm.nodesource.com/setup_11.x | sudo -E bash -",
  "sudo yum -y install nodejs",
  "wget http://bit.ly/2vESNuc -O /home/ec2-user/helloworld.js",
  "node /home/ec2-user/helloworld.js"
]))

t.add_resource(ec2.Instance(
  "instance",
  ImageId="ami-0ae254c8a2d3346a7",
  InstanceType="t2.micro",
  SecurityGroups=[Ref("SecurityGroup")],
  KeyName=Ref("KeyPair"),
  UserData=ud,
))

t.add_output(Output(
  "InstancePublicIp",
  Description="Public IP of instance.",
  Value=GetAtt("instance", "PublicIp"),
))

t.add_output(Output(
  "WebUrl",
  Description="App endpoint",
  Value=Join("", [
    "http://", GetAtt("instance", "PublicDnsName"),
    ":", ApplicationPort
  ]),
))

print (t.to_json())