# 389 Directory Server

#### How to create the template INF file
```bash
  /usr/lib/python3.10/site-packages/usr/sbin/dscreate create-template template.inf
```

#### Create instance from template

```bash
  /usr/lib/python3.10/site-packages/usr/sbin/dscreate from-file /etc/dirsrv/template.inf
```