FROM ubuntu:16.04

RUN apt-get update && apt-get install -y openssh-server git python3 iputils-ping net-tools wget
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py
RUN pip install paramiko
RUN git clone https://github.com/molpako/blackhat-python.git
RUN mkdir /var/run/sshd
RUN echo 'root:screencast' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22
EXPOSE 9999
CMD ["/usr/sbin/sshd", "-D"]
