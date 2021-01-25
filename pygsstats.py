import geoip2.database
import xml.etree.ElementTree as ET
import subprocess


PYGSS = {
    'CLIENT_ADDRESS': "pkapi::network::UdpSocket::UpdateToAddress: New client address"
}

# Read VM names from GameServer config
def get_servers(path="/usr/local/etc/gameserver/conf.xml"):
    tree = ET.parse(path)
    root = tree.getroot()
    vms = []
    for server in root.iter('Server'):
        vms.append(server.get('name'))
    return vms


# Wrapper for shell command excecution
def exec_shell_command(command, split=True):
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    stdout, stderr = proc.communicate()
    if split:
        return stdout.split('\n')
    else:
        return stdout 


# Read GameServer log for <vm> for <start>-<end> timeframe.
def get_log(domainName, start, end, split=True, reverse=False, debug=False, logdir=''):
    jctl_options = ["-o short-iso"]
    jctl_options.append("--no-pager -tgameserver/{}".format(domainName))

    if start:
        jctl_options.append("--since=\"{}\"".format(start))
    if end:
        jctl_options.append("--until=\"{}\"".format(end))
    if reverse:
        jctl_options.append("-r")
    if logdir:
        jctl_options.append("--directory {}".format(logdir))

    jctl = "journalctl {}".format(" ".join(jctl_options))
    if debug:
        print('Get journal: {}'.format(jctl))
    data = exec_shell_command(jctl, split)

    return data

# Read GameServer log for all vms for <start>-<end> timeframe.
def get_log_all(start, end, split=True, reverse=False, debug=False, logdir=''):
    jctl_options = ["-o short-iso"]
    jctl_options.append("--no-pager -u gameserver")

    if start:
        jctl_options.append("--since=\"{}\"".format(start))
    if end:
        jctl_options.append("--until=\"{}\"".format(end))
    if reverse:
        jctl_options.append("-r")
    if logdir:
        jctl_options.append("--directory {}".format(logdir))

    jctl = "journalctl {}".format(" ".join(jctl_options))
    if debug:
        print('Get journal: {}'.format(jctl))
    data = exec_shell_command(jctl, split)

    return data


# Get IP address location info using MaxMind databases
def get_location(ipaddress):
    reader = geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-City.mmdb')
    readerasn = geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-ASN.mmdb')
    result = {}
    try:
        location = reader.city(ipaddress)
        result["Continent"] = location.continent.name.encode('ascii', 'replace')
        result["Country"] = location.country.name.encode('ascii', 'replace')
        result["Region"] = location.subdivisions.most_specific.name.encode('ascii', 'replace')
        result["City"] = location.city.name.encode('ascii', 'replace')
        result["Latitude"] = float(location.location.latitude)
        result["Longitude"] = float(location.location.longitude)
        asn = readerasn.asn(ipaddress)
        result["ASN"] = "AS{}".format(asn.autonomous_system_number)
        result["ASN Provider"] = asn.autonomous_system_organization.encode('ascii', 'replace')
    except geoip2.errors.AddressNotFoundError:
        pass
    except AttributeError:
        pass
    reader.close()
    readerasn.close()
    return result

def find_all(sub, string):
    index = 0 - len(sub)
    try:
        while True:
            index = string.index(sub, index + len(sub))
            yield index
    except ValueError:
        pass
