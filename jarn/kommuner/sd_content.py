import re, htmlentitydefs

from jarn.kommuner import sd_client


def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    if text:
        return re.sub("&#?\w+;", fixup, text)
    else:
        return ''

def unparagraph(text):
    match = re.match("<p>(.*?)</p>", text)
    if match is None:
        return text
    return match.group(1)


def importActiveServiceDescriptions(context):
    ct = context.portal_catalog
    active_sd_ids = [sd['tjenestebeskrivelseID']
                     for sd in sd_client.getActiveServiceDescriptionsOverview()]
    for sd_id in active_sd_ids:
        sd = sd_client.getServiceDescription(sd_id)

        title = sd['navn'].encode('utf-8')


        description = unparagraph(unescape(sd['ingress'])).encode('utf-8') if 'ingress' in sd else ''

        general = {
            'htmlDescription': unescape(sd['beskrivelse']).encode('utf-8'),
            'targetGroup': unescape(sd['malgruppe']).encode('utf-8'),
            'criteria':  unescape(sd['kriterier']).encode('utf-8'),
            'price': unescape(sd['pris']).encode('utf-8'),
            'partners': unescape(sd['partnere']).encode('utf-8'),
            'brochures': unescape(sd['brosjyrer']).encode('utf-8'),
        }

        application = {
            'guidelines': unescape(sd['soknadVeiledning']).encode('utf-8'),
            'attachment': unescape(sd['soknadVedlegg']).encode('utf-8'),
            'form': unescape(sd['soknadSkjema']).encode('utf-8'),
            'recipient': unescape(sd['soknadMottaker']).encode('utf-8'),
            'notes': unescape(sd['soknadMerknader']).encode('utf-8'),
            'complaint': unescape(sd['soknadKlage']).encode('utf-8'),
            'deadline': unescape(sd['soknadFrist']).encode('utf-8'),
            'duration': unescape(sd['soknadBehandlingstid']).encode('utf-8'),
            'processing': unescape(sd['soknadBehandling']).encode('utf-8'),
        }

        laws = []
        if 'dokumentRef' in sd:
            doc_refs = sd['dokumentRef']
            for doc_ref in doc_refs:
                if doc_ref['dokumenttypeID'] in [1,2,3,8]:
                    ref = {
                        'title': doc_ref['tittel'].encode('utf-8'),
                        'url': doc_ref['uri'],
                        'description': doc_ref['beskrivelse'] if 'beskrivelse' in doc_ref else ''
                    }
                    laws.append(ref)

        other = {
            'updated': sd['datoOppdatert'],
            'valid_from': sd['gyldigFra'] if 'gyldigFra' in sd else '',
            'state': sd['livsITRefs'] if 'livsITRefs' in sd else []
        }

        normalized_word_ids = [ref['psi'].replace('emneord', 'ord') for ref in sd['emneordRefs']]
        topic_refs = ct.searchResults(synonymIds={'query': normalized_word_ids, 'operator': 'or'})
