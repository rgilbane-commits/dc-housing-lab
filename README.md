# DC Housing Lab v1.3.3 — Capital Stack Visualization

This is a drop-in upgrade to v1.3.2. It adds a sources-and-uses stacked bar diagram, a detailed capital sources table, and CSV export under **Build a project**.

## Deployment
Extract the ZIP. In your GitHub repository, upload the CONTENTS of the `DC_Housing_Lab_v1.3.3` folder to repository root and commit to your Streamlit-connected branch. Keep `.streamlit/config.toml` if already present. Run `python -m unittest discover -s tests -v` to repeat QC. Then open the Streamlit Cloud URL and verify **v1.3.3**, the capital stack and its download button. To roll back, revert the GitHub commit.

## Visualization methodology
Uses = net development cost after the hypothetical public land discount. Available capital sources = cash grants + public loans + supportable modeled private permanent debt + entered committed equity. An unfunded amount appears in red. If available capital exceeds uses, the excess is explicitly disclosed (it is not profit), and the bar shows all available sources. Requested private debt above supportable capacity is excluded. All values use the same dollar scale. The capital stack is not a schedule of funding draws, lender approval, construction financing, or IRR analysis.

Inputs are hypothetical educational assumptions, not verified Washington, DC market values or official AMI limits.
