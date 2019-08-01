# crtsh_scanner
A tool to discover domains using crt.sh site.

# Install
```console
pip install -r requirements.txt
```

# Usage
```console
usage: crtsh_scanner.py [-h] --domain N [N ...] [--extended]
                        [--exclude_expired] [--uncached]

Discover domains using crt.sh.

optional arguments:
  -h, --help            show this help message and exit
  --domain N [N ...], -d N [N ...]
                        crt.sh domain query. Specify multiple using --domain
                        <domain>
  --extended            include wildcard searches with domain private suffix
                        ('google.%.%' for 'google.com').
  --exclude_expired     Exclude expired certificates.
  --uncached            Only return domains not previously discovered (not in
                        PEM cache).
```

# Example
Discover domains from SSL certificate SAN (Subject Alternate Name) field.
```console
$ python crtsh_scanner.py -d example.com
Domain: ['example.com'], Extended: False, Exclude Expired: False, Uncached: False
https://crt.sh/?output=json&Identity=example.com
New domains found: 8.  Total: 8
New domains found: 2.  Total: 10
New domains found: 1.  Total: 11
New domains found: 1.  Total: 12
New domains found: 3.  Total: 15
{'*.test1.com', 'www.example.net', 'support.example.com', 'example.net', 'm.example.com', 'm.testexample.com',
'dev.example.com', 'example.org', 'example.edu', 'example.com', 'www.example.com', '*.example.com', 'www.example.org',
'products.example.com', 'www.example.edu'}
```

Exclude expired certificates in domain discovery.
```console
$ python crtsh_scanner.py -d example.com --exclude_expired
Domain: ['example.com'], Extended: False, Exclude Expired: True, Uncached: False
https://crt.sh/?output=json&exclude=expired&Identity=example.com
New domains found: 8.  Total: 8
{'www.example.com', 'example.net', 'example.edu', 'example.com', 'www.example.net', 'www.example.org', 'example.org', 'www.example.edu'}
```

Discover only previous unseen domains.  This is useful when the script is run on an on-going basis and set to alert for new domains.
```console
$ python crtsh_scanner.py -d example.com --uncached
Domain: ['example.com'], Extended: False, Exclude Expired: False, Uncached: True
https://crt.sh/?output=json&Identity=example.com
New domains found: 4.  Total: 4
{'m.testexample.com', '*.test1.com', 'example.com', 'www.example.com'}
```

Include crt.sh wildcard searches in domain discovery.  Depending on how domain name, this could result in a large number of results.
```console
$ python crtsh_scanner.py -d crizal.com --extended
Domain: ['crizal.com'], Extended: True, Exclude Expired: False, Uncached: False
https://crt.sh/?output=json&Identity=crizal.com
New domains found: 45.  Total: 45
https://crt.sh/?output=json&q=crizal.%25.%25
New domains found: 2.  Total: 2
New domains found: 2.  Total: 4
New domains found: 2.  Total: 6
New domains found: 2.  Total: 8
{'crizal.com.br', 'www.essilorpro.nl', 'www.essilorpro.no', 'www.essilorpro.fi', 'www.admin.eservices.essilor.com', 'www.essilorpro.dk', 'admin.eservices.bbgr.com', 'admin.eservices.essilor.com', 'bbgr.med-cis.com', 'www.essilor.hu', 'www.essilor.rs', 'www.essilor.cz', 'www.essilor.de', 'www.varilux.com.tr', 'www.crizal.com.br', 'www.bbgr.es', 'www.essilor.bg', 'tracking.essilor.ch', 'www.crizal.de', 'crizal.com.ar', 'crizal.com', 'www.essilor.co.il', 'admin.valoptec.com', 'www.essilor.ch', 'www.essilorpro.se', 'www.xperio.es', 'crizal.co.za', 'www.essilorpro.es', 'www.crizal.es', 'www.essilor.si', 'www.crizal.co.za', 'essilor.ca', 'www.optifog.de', 'eyestation.bbgr.com', 'www.crizal.com.tr', 'www.valoptec.com', 'www.essilor.med-cis.com', 'www.essilor.pl', 'www.xperio.de', 'www.essilorpro.co.uk', 'www.eyezen.de', 'www.essilor.hr', 'www.essilorpro.de', 'www.essilor.ro', 'www.crizal.com', 'essilor.med-cis.com', 'crizal.com.tr', 'www.essilor.sk', 'www.essilorpro.be', 'www.essilorpro.pt', 'www.essilor.ca', '*.crizal.com.ar'}
```

