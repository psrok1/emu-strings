import requests
import os
import sys
from pdbparse.peinfo import *

SYM_SRVS = ['http://msdl.microsoft.com/download/symbols']
USER_AGENT = "Microsoft-Symbol-Server/6.11.0001.404"

def download_pdb(guid, fname):
    session = requests.Session()
    session.headers = {
        "User-Agent": USER_AGENT
    }

    for sym_srv in SYM_SRVS:
        sym_base = sym_srv + "/{}/{}/".format(fname, guid)
        variants = [fname[:-1]+"_", fname]
        for v in variants:
            sym_url = sym_base + v
            print "Trying {}".format(sym_url)
            outfile = session.get(sym_url)
            if outfile.status_code == 200:
                print "Saved symbols to {}".format(v)
                with open(v, "wb") as f:
                    f.write(outfile.content)
                return v
            else:
                print "HTTP Error {}".format(outfile.status_code)
    return None

def download_pdb_by_pe(pe_file):
    dbgdata, tp = get_pe_debug_data(pe_file)
    if tp == "IMAGE_DEBUG_TYPE_CODEVIEW":
        # XP+
        if dbgdata[:4] == b"RSDS":
            (guid,filename) = get_rsds(dbgdata)
        elif dbgdata[:4] == b"NB10":
            (guid,filename) = get_nb10(dbgdata)
        else:
            raise Exception("ERR: CodeView section not NB10 or RSDS")
        guid = guid.upper()
        saved_file = download_pdb(guid, filename)
    elif tp == "IMAGE_DEBUG_TYPE_MISC":
        # Win2k
        # Get the .dbg file
        guid = get_pe_guid(pe_file)
        guid = guid.upper()
        filename = get_dbg_fname(dbgdata)
        saved_file = download_pdb(guid, filename)

        # Extract it if it's compressed
        # Note: requires cabextract!
        if saved_file.endswith("_"):
            os.system("cabextract %s" % saved_file)
            saved_file = saved_file.replace('.db_','.dbg')

        from pdbparse.dbgold import DbgFile
        dbgfile = DbgFile.parse_stream(open(saved_file, 'rb'))
        cv_entry = [ d for d in dbgfile.IMAGE_DEBUG_DIRECTORY
                       if d.Type == "IMAGE_DEBUG_TYPE_CODEVIEW"][0]
        if cv_entry.Data[:4] == b"NB09":
            return
        elif cv_entry.Data[:4] == b"NB10":
            (guid,filename) = get_nb10(cv_entry.Data)
            
            guid = guid.upper()
            saved_file = download_pdb(guid, filename)
        else:
            raise Exception("DBG file received from symbol server has unknown CodeView section")
    else:
        raise Exception("Unknown type: {}".format(tp))

    if saved_file != None and saved_file.endswith("_"):
        os.system("cabextract %s" % saved_file)

if __name__ == "__main__":
    download_pdb_by_pe(sys.argv[1])
