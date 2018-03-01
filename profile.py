#!/usr/bin/env python

"""
NOTE: This profile tracks more recent versions of OAI (develop branch),
      and is likely to change more frequently.

Use this profile to instantiate an experiment using Open Air Interface
to realize an end-to-end SDR-based mobile network. This profile includes
the following resources:

  * Off-the-shelf Nexus 5 UE running Android 4.4.4 KitKat ('rue1')
  * SDR eNodeB (Intel NUC + USRP B210) running OAI on Ubuntu 16 ('enb1')
  * All-in-one EPC node (HSS, MME, SPGW) running OAI on Ubuntu 16 ('epc')
  * A node providing out-of-band ADB access to the UE ('adb-tgt')

PhantomNet startup scripts automatically configure OAI for the
specific allocated resources.

For more detailed information:

  * [Getting Started](https://gitlab.flux.utah.edu/duerig/oai-enb/blob/master/README.md)
  * [Controlling OAI](https://gitlab.flux.utah.edu/duerig/oai-enb/blob/master/control.md)
  * [Inspecting OAI](https://gitlab.flux.utah.edu/duerig/oai-enb/blob/master/inspect.md)
  * [Modifying OAI](https://gitlab.flux.utah.edu/duerig/oai-enb/blob/master/modify.md)

"""

#
# Standard geni-lib/portal libraries
#
import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.emulab as elab
import geni.rspec.igext
import geni.urn as URN

#
# PhantomNet extensions.
#
import geni.rspec.emulab.pnext as PN

#
# Globals
#
class GLOBALS(object):
    OAI_DS = "urn:publicid:IDN+emulab.net:phantomnet+ltdataset+oai-develop"
    UE_IMG  = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:ANDROID444-STD")
    ADB_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU14-64-PNTOOLS")
    OAI_EPC_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU16-64-OAIEPC")
    OAI_ENB_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU16-64-OAIENB")
    OAI_CONF_SCRIPT = "/usr/bin/sudo /local/repository/bin/config_oai.pl"
    NUC_HWTYPE = "nuc5300"
    UE_HWTYPE = "nexus5"

def connectOAI_DS(node):
    # Create remote read-write clone dataset object bound to OAI dataset
    bs = request.RemoteBlockstore("ds-%s" % node.name, "/opt/oai")
    bs.dataset = GLOBALS.OAI_DS
    bs.rwclone = True

    # Create link from node to OAI dataset rw clone
    node_if = node.addInterface("dsif_%s" % node.name)
    bslink = request.Link("dslink_%s" % node.name)
    bslink.addInterface(node_if)
    bslink.addInterface(bs.interface)
    bslink.vlan_tagging = True
    bslink.best_effort = True

#
# This geni-lib script is designed to run in the PhantomNet Portal.
#
pc = portal.Context()

#
# Profile parameters.
#
pc.defineParameter("FIXED_UE", "Bind to a specific UE",
                   portal.ParameterType.STRING, "",
                   longDescription="Input the name of a PhantomNet UE node to allocate (e.g., \'ue1\').  Leave blank to let the mapping algorithm choose.")
pc.defineParameter("FIXED_ENB", "Bind to a specific eNodeB",
                   portal.ParameterType.STRING, "",
                   longDescription="Input the name of a PhantomNet eNodeB device to allocate (e.g., \'nuc1\').  Leave blank to let the mapping algorithm choose.  If you bind both UE and eNodeB devices, mapping will fail unless there is path between them via the attenuator matrix.")

pc.defineParameter("RADIATEDRF", "Radiated (over-the-air) RF transmissions",
                   portal.ParameterType.BOOLEAN, False,
                   longDescription="When enabled, RF devices with real antennas and transmissions propagated through free space will be selected.  Leave disabled (default) to assign RF devices connected via transmission lines with variable attenuator control.")

params = pc.bindParameters()

#
# Give the library a chance to return nice JSON-formatted exception(s) and/or
# warnings; this might sys.exit().
#
pc.verifyParameters()

#
# Create our in-memory model of the RSpec -- the resources we're going
# to request in our experiment, and their configuration.
#
request = pc.makeRequestRSpec()

# Add a node to act as the ADB target host
adb_t = request.RawPC("adb-tgt")
adb_t.disk_image = GLOBALS.ADB_IMG

# Add OAI EPC (HSS, MME, SPGW) node.
epc = request.RawPC("epc")
epc.disk_image = GLOBALS.OAI_EPC_IMG
epc.addService(rspec.Execute(shell="sh", command=GLOBALS.OAI_CONF_SCRIPT + " -r EPC"))
connectOAI_DS(epc)

# Add a NUC eNB node.
enb1 = request.RawPC("enb1")
if params.FIXED_ENB:
    enb1.component_id = params.FIXED_ENB
enb1.hardware_type = GLOBALS.NUC_HWTYPE
enb1.disk_image = GLOBALS.OAI_ENB_IMG
enb1.Desire( "rf-radiated" if params.RADIATEDRF else "rf-controlled", 1 )
connectOAI_DS(enb1)
enb1.addService(rspec.Execute(shell="sh", command=GLOBALS.OAI_CONF_SCRIPT + " -r ENB"))
enb1_rue1_rf = enb1.addInterface("rue1_rf")

# Add an OTS (Nexus 5) UE
rue1 = request.UE("rue1")
if params.FIXED_UE:
    rue1.component_id = params.FIXED_UE
rue1.hardware_type = GLOBALS.UE_HWTYPE
rue1.disk_image = GLOBALS.UE_IMG
rue1.Desire( "rf-radiated" if params.RADIATEDRF else "rf-controlled", 1 )
rue1.adb_target = "adb-tgt"
rue1_enb1_rf = rue1.addInterface("enb1_rf")

# Create the RF link between the Nexus 5 UE and eNodeB
rflink2 = request.RFLink("rflink2")
rflink2.addInterface(enb1_rue1_rf)
rflink2.addInterface(rue1_enb1_rf)

# Add a link connecting the NUC eNB and the OAI EPC node.
epclink = request.Link("s1-lan")
epclink.addNode(enb1)
epclink.addNode(epc)
epclink.link_multiplexing = True
epclink.vlan_tagging = True
epclink.best_effort = True

#
# Print and go!
#
pc.printRequestRSpec(request)
