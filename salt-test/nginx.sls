#ensure that the proper repo is found on the machine
nginx-ppa:
  pkgrepo.managed:
    - name: ppa:nginx/stable
    - require_in: nginx

#Make sure the package is installed and latest version is used
nginx:
  pkg.latest:
    - refresh: True
#ensure the the service is running, and that it will start upon reboot
  service.running:
    - reload: True
    - enable: True
    - watch:
#watch for changes in the package, and reload if there are any
      - pkg: nginx

#create the root and error directory
create_dirs:
  file.directory:
    - user: root
    - group: root
    - mode: 755
    - makedirs: True
    - names:
      - /etc/nginx/www/
      - /etc/nginx/www/error/


#create the nginx config file on the minion, and copy the contents of the file from the salt-master.
/etc/nginx/nginx.conf:
  file.managed:
    - source: salt://nginx/nginx.conf
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - context:
      server_name: {{ grains.host }}

#Same as above, but with index.html
/etc/nginx/www/index.html:
  file.managed:
    - source: salt://nginx/index.html
    - user: root
    - group: root
    - mode: 644

#Same as above
/etc/nginx/www/error/404.html:
  file.managed:
    - source: salt://nginx/404.html
    - user: root
    - group: root
    - mode: 644