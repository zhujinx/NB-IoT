# EXPERIMENTAL PROFILE TO TEST SDR UE

# About This Profile

Be sure to setup your SSH keys as outlined in the manual; it's better
to log in via a real SSH client to the nodes in your experiment.

The Open Air Interface source is located under `/opt/oai` on the enb1
and epc nodes.  It is mounted as a clone of a remote blockstore
(dataset) maintained by PhantomNet.  Feel free to change anything in
here, but be aware that your changes will not persist when your
experiment terminates.

This experiment can work in two modes:
1. UE and eNodeB SDR
2. Simulated UE+eNodeB (OAISIM).

To enable OAISIM, select OAI_SIM in the drop down menu "Experiment Type"
while instantiating the experiment. When the experiment starts, two nodes
will be created: sim_enb and epc.

To get the SDR based eNodeB and off-the-shelf UE, select one of the other
two options in the "Experiment Type" based upon the requirements.

# Getting Started

Default configurations of UE subscription and Radio to use SDR-version UE. 

1. User subscription info  
imsi : 998981234560308  
algo : milenage  
opc   : 0ED47545168EAFE2C39C075829A7B61F   
k    : 00112233445566778899aabbccddeeff  
amf  : 8000  

2. LTE band : 4  

############################ Run OAI-CN ############################  
Access to `epc` node.

1. Provision UE in OAI-CN HSS  
$ cd  /local/repository/config/oai-db  
$ mysql -u root -p # password : linux  
``` bash
mysql> use oai_db  
mysql> INSERT INTO pdn (`id`, `apn`, `pdn_type`, `pdn_ipv4`, `pdn_ipv6`, `aggregate_ambr_ul`, `aggregate_ambr_dl`, `pgw_id`, `users_imsi`, `qci`, `priority_level`,`pre_emp_cap`,`pre_emp_vul`, `LIPA-Permissions`) VALUES ('3',  'oai.ipv4','IPV4', '0.0.0.0', '0:0:0:0:0:0:0:0', '50000000', '100000000', '2',  '998981234560308', '9', '15', 'DISABLED', 'ENABLED', 'LIPA-ONLY');   
mysql> INSERT INTO users (`imsi`, `msisdn`, `imei`, `imei_sv`, `ms_ps_status`, `rau_tau_timer`, `ue_ambr_ul`, `ue_ambr_dl`, `access_restriction`, `mme_cap`, `mmeidentity_idmmeidentity`, `key`, `RFSP-Index`, `urrp_mme`, `sqn`, `rand`, `OPc`) VALUES ('998981234560308',  '33638060308', NULL, NULL, 'PURGED', '120', '50000000', '100000000', '47', '0000000000', '1', 0x00112233445566778899aabbccddeeff, '1', '0', 0, 0x00000000000000000000000000000000, 0x0ED47545168EAFE2C39C075829A7B61F);   
```

After booting is complete, log onto either the `enb1` or `epc`
nodes. From there, you will be able to start all OAI services across
the network by running:

    sudo /local/repository/bin/start_oai.pl

This will stop any currently running OAI services, start all services
(both epc and enodeb) again, and then interactively show a tail of the
logs of the mme and enodeb services. Once you see the logs, you can
exit at any time with Ctrl-C, but the services stay running in the
background and save logs to `/var/log/oai/*` on the `enb1` and `epc`
nodes.

Start the OAI-UE at the UE node in /opt/oai/openairinterface-5g/target/bin/
sudo ./lte-softmodem.Rel14  -U -C 2120000000 --ue-txgain 70 --ue-rxgain 90 --ue-scan-carrier -r 25


The OAI mobile networking functions should automatically start up when
your experiment starts up.  You can pull up and monitor the OAI
processes on the `epc` and `enb1` nodes. Execute `sudo screen -ls` to
see what sessions are available. The commands for controlling services
on these nodes are located in `/local/repository/bin`.

OAI is a project that is in development. As such, it is not always
stable and there will be times when it gets into a failed state that
it can never recover from. Almost always, you will be able to bring
things back by either rebooting the experiment from the portal or
restarting the services by hand from the command line.

For more detailed information:

  * [Controlling OAI](https://gitlab.flux.utah.edu/powder-profiles/OAI-Real-Hardware/blob/master/control.md)
  * [Inspecting OAI](https://gitlab.flux.utah.edu/powder-profiles/OAI-Real-Hardware/blob/master/inspect.md)
  * [Modifying OAI](https://gitlab.flux.utah.edu/powder-profiles/OAI-Real-Hardware/blob/master/modify.md)
  * [Modifying This Profile](https://gitlab.flux.utah.edu/powder-profiles/OAI-Real-Hardware/blob/master/modify-profile.md)
