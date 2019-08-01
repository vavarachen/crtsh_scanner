import requests
from pathlib import Path
import ssl
from publicsuffixlist import PublicSuffixList
import argparse

STATE_DIR = Path('state')   # store pem files (cache)
STATE_DIR.mkdir(exist_ok=True)


def get_cert_ids(domain, args, extended=None):
    """ Find all certs found with 'domain' in the Identity section """
    base_url = "https://crt.sh/"
    r_params = {'output': "json"}

    if args.exclude_expired is True:
        r_params['exclude'] = 'expired'

    if (extended is None or extended is True) and args.extended is True:
        r_params['q'] = "{}.%.%".format(get_domain_private_suffix(domain))
    else:
        r_params['Identity'] = domain

    r_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
    req = requests.get(base_url, params=r_params, headers=r_headers)
    print(req.url)

    if req.ok:
        try:
            for cert in req.json():
                yield cert['min_cert_id']
        except Exception as err:
            print("Error retrieving information.")
    return None


def get_cert(cert_id, args):
    """ download the PEM formatted certificate for processing """
    pem_file = STATE_DIR.joinpath('%s.pem' % cert_id)
    if pem_file.exists():
        if args.uncached is True:
            return None

        return pem_file
    else:
        base_url = "https://crt.sh/?d={}"
        url = base_url.format(cert_id)

        ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
        req = requests.get(url, headers={'User-Agent': ua})

        if req.ok:
            try:
                pem_file.open('w+b').write(req.content)
                return pem_file
            except Exception as err:
                print("Error retrieving PEM.")
        return None


def get_subjectaltname(cert_path):
    """ Extract subjectAltName from the certificate."""
    # undocument ssl method follows
    if cert_path is None:
        pass
    else:
        pem = ssl._ssl._test_decode_cert(cert_path.as_posix())
        if 'subjectAltName' in pem.keys():
            for t in list(pem['subjectAltName']):
                if t[0] == 'DNS':
                    yield t[1]
        else:
            try:
                yield pem['commonName']
            except:
                yield ""


def get_subdomains(domain, args, extended=None):
    """ Extracts domain names from subjectAltName filed"""
    if extended is None:
        extended = args.extended
    subdomains = set()
    count = 0

    if extended:
        priv_suffix = get_domain_private_suffix(domain)

    for crtsh_id in get_cert_ids(domain, args, extended):
        for subject in get_subjectaltname(get_cert(crtsh_id, args)):
            if not extended:
                subdomains.add(subject.lower())
            elif subject.count(priv_suffix):
                subdomains.add(subject.lower())

        new_count = len(subdomains) - count
        if new_count > 0:
            print("New domains found: %d.  Total: %d" % (new_count, count + new_count))
        count = len(subdomains)

    return subdomains


def get_domain_private_suffix(domain):
    """ returns 'www.google' for 'www.google.com' """
    psl = PublicSuffixList()
    tld = "." + psl.publicsuffix(domain)
    return domain.replace(tld,'')


def main(args):
    print('Domain: %s, Extended: %s, Exclude Expired: %s, Uncached: %s'
          % (args.domain, args.extended, args.exclude_expired, args.uncached))
    if args.extended:
        for domain in args.domain:
            print(get_subdomains(domain, args, extended=False).union(get_subdomains(domain, args)))
    else:
        for domain in args.domain:
            print(get_subdomains(domain, args, extended=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Discover domains using crt.sh.")
    parser.add_argument('--domain', '-d', required=True, metavar='N', type=str, nargs='+',
                        help="crt.sh domain query.  Specify multiple using --domain <domain>")
    parser.add_argument('--extended', required=False, default=False, action='store_true',
                        help="include wildcard searches with domain private suffix ('google.%%.%%' for 'google.com').")
    parser.add_argument('--exclude_expired', required=False, default=False, action='store_true',
                        help="Exclude expired certificates.")
    parser.add_argument('--uncached', required=False, default=False, action='store_true',
                        help="Only return domains not previously discovered (not in PEM cache).")
    parser.set_defaults(func=main)

    try:
        args = parser.parse_args()
        args.func(args)
    except Exception as err:
        print(err)
        parser.print_help()
