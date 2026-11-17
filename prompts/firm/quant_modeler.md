# firm.quant_modeler

The quant modeler runs no language model. Every number in the engagement (scoring matrices, price
statistics, waitlist targets, threshold comparisons, role costs against budget, pricing tiers) is
computed by the calculator in `app/tools.py` from validated inputs. Model text is never evaluated as
code. Inputs that are not sourced are carried through as ASSUMPTION.
