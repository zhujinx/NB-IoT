#!/usr/bin/env python

#
# Standard geni-lib/portal libraries
#
import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.emulab as elab
import geni.rspec.igext as IG
import geni.urn as URN


tourDescription = """

# EXPERIMENTAL PROFILE TO TEST SDR UE

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

  * [Getting Started](https://gitlab.flux.utah.edu/powder-profiles/OAI-Real-Hardware/blob/master/README.md)

""";

tourInstructions = """
After booting is complete,
For Simulated UE, log onto `epc` node and run:

    sudo /local/repository/bin/start_oai.pl -r sim

Else, log onto either the `enb1` or `epc` nodes. From there, you will be able to start all OAI services across the network by running:

    sudo /local/repository/bin/start_oai.pl

Above command will stop any currently running OAI services, start all services (both epc and enodeb) again, and then interactively show a tail of the logs of the mme and enodeb services. Once you see the logs, you can exit at any time with Ctrl-C, but the services stay running in the background and save logs to `/var/log/oai/*` on the `enb1` and `epc` nodes.

Once all the services are running, the UE device will typically connect on its own, but if it doesn't you can reboot the phone. You can manage the UE by logging into the `adb-tgt` node, running `pnadb -a` to connect, and then managing it via any `adb` command such as `adb shell` or `adb reboot`.

For Simulated UE experiment, check the connectivity by logging into the `sim-enb` node and run:

    ping -I oip1 8.8.8.8

While OAI is still a system in development and may be unstable, you can usually recover from any issue by running `start_oai.pl` to restart all the services.

  * [Full Documentation](https://gitlab.flux.utah.edu/powder-profiles/OAI-Real-Hardware/blob/master/README.md)

""";


#
# PhantomNet extensions.
#
import geni.rspec.emulab.pnext as PN

#
# Globals
#
class GLOBALS(object):
    OAI_DS = "urn:publicid:IDN+emulab.net:powdersandbox+ltdataset+NB-IoT"
    OAI_UE_DS = "urn:publicid:IDN+emulab.net:powdersandbox+ltdataset+NB-IoT-UE"
    OAI_EPC_DS="urn:publicid:IDN+emulab.net:powdersandbox+ltdataset+OAI'
    OAI_SIM_DS = "urn:publicid:IDN+emulab.net:phantomnet+dataset+PhantomNet:oai"
    UE_IMG  = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:ANDROID444-STD")
    ADB_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU14-64-PNTOOLS")
    OAI_EPC_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU16-64-OAIEPC")
    OAI_ENB_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:OAI-Real-Hardware.enb1")
    OAI_SIM_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU14-64-OAI")
    OAI_CONF_SCRIPT = "/usr/bin/sudo /local/repository/bin/config_oai.pl"
    SIM_HWTYPE = "d430"
    NUC_HWTYPE = "nuc5300"
    UE_HWTYPE = "nexus5"

def connectOAI_DS(node, type):
    # Create remote read-write clone dataset object bound to OAI dataset
    bs = request.RemoteBlockstore("ds-%s" % node.name, "/opt/oai")
    if type == 1:
	bs.dataset = GLOBALS.OAI_UE_DS
    else if type ==2:
	bs.dataset = GLOBALS.OAI_EPC_DS
    else
        bs.dataset = GLOBALS.OAI_DS
    #bs.rwclone = True

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
                   portal.ParameterType.STRING, "", advanced=True,
                   longDescription="Input the name of a PhantomNet UE node to allocate (e.g., 'ue1').  Leave blank to let the mapping algorithm choose.")
pc.defineParameter("FIXED_ENB", "Bind to a specific eNodeB",
                   portal.ParameterType.STRING, "", advanced=True,
                   longDescription="Input the name of a PhantomNet eNodeB device to allocate (e.g., 'nuc1').  Leave blank to let the mapping algorithm choose.  If you bind both UE and eNodeB devices, mapping will fail unless there is path between them via the attenuator matrix.")

pc.defineParameter("TYPE", "Experiment type",
                   portal.ParameterType.STRING,"ota",[("sim","Simulated UE"),("atten","Real UE with attenuator"),("ota","Over the air")],
                   longDescription="*Simulated UE*: OAI simulated UE connects to an OAI eNodeB and EPC. *Real UE with attenuator*: Real RF devices will be connected via transmission lines with variable attenuator control. *Over the air*: Real RF devices with real antennas and transmissions propagated through free space will be selected.")

#pc.defineParameter("RADIATEDRF", "Radiated (over-the-air) RF transmissions",
#                   portal.ParameterType.BOOLEAN, False,
#                   longDescription="When enabled, RF devices with real antennas and transmissions propagated through free space will be selected.  Leave disabled (default) to assign RF devices connected via transmission lines with variable attenuator control.")

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
epclink = request.Link("s1-lan")

# Checking for oaisim

if params.TYPE == "sim":
    sim_enb = request.RawPC("sim-enb")
    sim_enb.disk_image = GLOBALS.OAI_SIM_IMG
    sim_enb.hardware_type = GLOBALS.SIM_HWTYPE
    sim_enb.addService(rspec.Execute(shell="sh", command=GLOBALS.OAI_CONF_SCRIPT + " -r SIM_ENB"))
    connectOAI_DS(sim_enb, 1)
    epclink.addNode(sim_enb)
else:
    # Add a node to act as the ADB target host
    #adb_t = request.RawPC("adb-tgt")
    #adb_t.disk_image = GLOBALS.ADB_IMG

    # Add a NUC eNB node.
    enb1 = request.RawPC("enb1")
    if params.FIXED_ENB:
        enb1.component_id = params.FIXED_ENB
    enb1.hardware_type = GLOBALS.NUC_HWTYPE
    enb1.disk_image = GLOBALS.OAI_ENB_IMG
    enb1.Desire( "rf-radiated" if params.TYPE == "ota" else "rf-controlled", 1 )
    connectOAI_DS(enb1, 0)
    enb1.addService(rspec.Execute(shell="sh", command=GLOBALS.OAI_CONF_SCRIPT + " -r ENB"))
    enb1_rue1_rf = enb1.addInterface("rue1_rf")

    # Add an OTS (Nexus 5) UE
    rue1 = request.RawPC("rue1")
    if params.FIXED_UE:
        rue1.component_id = params.FIXED_UE
    rue1.hardware_type = GLOBALS.NUC_HWTYPE
    rue1.disk_image = GLOBALS.OAI_ENB_IMG
    rue1.Desire( "rf-radiated" if params.TYPE == "ota" else "rf-controlled", 1 )
    connectOAI_DS(rue1, 1)
    enb1.addService(rspec.Execute(shell="sh", command=GLOBALS.OAI_CONF_SCRIPT + " -r UE"))
    rue1_enb1_rf = rue1.addInterface("enb1_rf")

    # Create the RF link between the Nexus 5 UE and eNodeB
    rflink2 = request.RFLink("rflink2")
    rflink2.addInterface(enb1_rue1_rf)
    rflink2.addInterface(rue1_enb1_rf)

    # Add a link connecting the NUC eNB and the OAI EPC node.
    epclink.addNode(enb1)

# Add OAI EPC (HSS, MME, SPGW) node.
epc = request.RawPC("epc")
epc.disk_image = GLOBALS.OAI_EPC_IMG
epc.addService(rspec.Execute(shell="sh", command=GLOBALS.OAI_CONF_SCRIPT + " -r EPC"))
connectOAI_DS(epc, 2)
 
epclink.addNode(epc)
epclink.link_multiplexing = True
epclink.vlan_tagging = True
epclink.best_effort = True

tour = IG.Tour()
tour.Description(IG.Tour.MARKDOWN, tourDescription)
tour.Instructions(IG.Tour.MARKDOWN, tourInstructions)
request.addTour(tour)

#
# Print and go!
#
pc.printRequestRSpec(request)
