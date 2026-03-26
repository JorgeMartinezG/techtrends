# set up the default terminal
ENV["TERM"]="linux"

# set minimum version for Vagrant
Vagrant.require_version ">= 2.2.10"
Vagrant.configure("2") do |config|
  config.vm.provision "shell",
    inline: "sudo su - && zypper update && zypper install -y apparmor-parser"
  
  # Set the image for the vagrant box
  config.vm.box = "opensuse/Leap-15.2.x86_64"
  # Set the image version
  config.vm.box_version = "15.2.31.632"

  # Forward the ports from the guest VM to the local host machine
  # Forward more ports, as needed
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 6111, host: 6111
  config.vm.network "forwarded_port", guest: 6112, host: 6112

  # ArgoCD UI (desde el host del lab)
  config.vm.network "forwarded_port", guest: 30188, host: 8080, host_ip: "127.0.0.1", auto_correct: true
  config.vm.network "forwarded_port", guest: 31728, host: 8443, host_ip: "127.0.0.1", auto_correct: true

  # Set the static IP for the vagrant box
  config.vm.network "private_network", ip: "192.168.50.4"
  
  # Configure the parameters for VirtualBox provider
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = 4
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
  end
end