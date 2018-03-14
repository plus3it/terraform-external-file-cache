locals {
  uri_map = {
    "https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm" = "/tmp/"
  }

  uris  = "${keys(local.uri_map)}"
  paths = "${values(local.uri_map)}"
}

module "file_cache" {
  source = "../../"

  uris = "${local.uris}"
}

data "http" "ip" {
  # Get local ip for security group ingress
  url = "http://ipv4.icanhazip.com"
}

data "aws_vpc" "example" {
  default = "true"
}

data "aws_ami" "example" {
  most_recent = true

  filter {
    name   = "name"
    values = ["amzn-ami-hvm-2017.09.*-x86_64-gp2"]
  }

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }

  name_regex = "amzn-ami-hvm-2017\\.09\\.\\d\\.[\\d]{8}-x86_64-gp2"
}

resource "tls_private_key" "example" {
  algorithm = "RSA"
  rsa_bits  = "4096"
}

resource "aws_key_pair" "example" {
  key_name_prefix = "terraform-external-file-cache-"
  public_key      = "${tls_private_key.example.public_key_openssh}"
}

resource "aws_security_group" "example" {
  name_prefix = "terraform-external-file-cache-"
  vpc_id      = "${data.aws_vpc.example.id}"

  tags {
    Name = "terraform-external-file-cache-example"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.ip.body)}/32"]
  }

  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "example" {
  ami                    = "${data.aws_ami.example.id}"
  instance_type          = "t2.micro"
  key_name               = "${aws_key_pair.example.id}"
  vpc_security_group_ids = ["${aws_security_group.example.id}"]

  tags {
    Name = "terraform-external-file-cache-example"
  }
}

resource "null_resource" "example" {
  count = "${length(module.file_cache.filepaths)}"

  connection {
    host        = "${aws_instance.example.public_ip}"
    port        = 22
    user        = "ec2-user"
    private_key = "${tls_private_key.example.private_key_pem}"
  }

  provisioner "file" {
    source      = "${element(module.file_cache.filepaths, count.index)}"
    destination = "${element(local.paths, count.index)}${basename(element(module.file_cache.filepaths, count.index))}"
  }
}

output "public_ip" {
  description = "Public IP of the EC2 instance"
  value       = "${aws_instance.example.public_ip}"
}

output "private_key" {
  description = "Private key for the keypair"
  value       = "${tls_private_key.example.private_key_pem}"
}

output "filepaths" {
  description = "List of cached filepaths retrieved from URIs"
  value       = ["${module.file_cache.filepaths}"]
}
