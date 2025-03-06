echo "
[windows]
$1

[windows:vars]
ansible_user=ltuser
ansible_password=#lambdapass123#
ansible_connection=psrp
ansible_psrp_port=5985
ansible_psrp_cert_trust_path=ignore
ansible_psrp_cert_validation=ignore
" >> inventory.ini
