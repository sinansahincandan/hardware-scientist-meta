# Notices

The code in this repository is MIT-licensed (see `LICENSE`). It contains no model weights.

**Models (main branch, for comparison).** At run time Hardware Engineer calls Meta models through the Meta Model API: Muse Spark 1.3
(all reasoning roles), Muse Image 1.0 (pictures) and SAM 3.1 (part maps). Use of those models is governed by Meta's
Model API terms and usage policies, which every user accepts with their own API key; nothing in this repository changes
them. Generated designs and pictures are model outputs; check them before you rely on them (see "Known limitations"
in `README.md`).

**Open-weights branch (`open-weights`).** That copy runs on Meta's open-weights **Muse Spark Open** (hosted on
Baseten) and **SAM 3** (run on Modal). It is **Built with Muse Spark Open**, as the Muse Model License requires
(<https://huggingface.co/meta-models/Muse-Spark-Open-816B-A42B>), and SAM 3 is used under the SAM License
(`licenses/SAM_LICENSE.txt`, from <https://github.com/facebookresearch/sam3>). Neither branch
redistributes model weights.

**Third-party work.** The method draws on published research; each work is cited in `README.md` ("Related work").
