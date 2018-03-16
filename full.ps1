Param([string]$loglevel="info")

echo "Log level set as $loglevel"

$aws_default_region="us-west-2"

$container_aws_dir="/root/.aws"
$container_ssh_dir="/root/.ssh"

$local_aws_dir="$home\.aws"
$local_ssh_dir="$home\.ssh"

echo "Contents of$local_aws_dir dir: $(Get-ChildItem $local_aws_dir)"
echo "Contents of $local_aws_dir/credentials dir: $(Get-Content $local_aws_dir/credentials)"

$container_name="default-vpc-killer"
$image_name="default-vpc-killer"

echo "Building Docker image: $image_name"
docker build -t $image_name .

docker run -i -t --rm `
    --name $image_name `
    -v "$local_aws_dir`:$container_aws_dir" `
    -v "$local_ssh_dir`:$container_ssh_dir" `
    -e "AWS_DEFAULT_REGION=$aws_default_region" `
    -e "dry_run=False" `
    -e "log_level=$loglevel" `
    $image_name