"""Transparent illustrative public support economics, independent of project finance calculations."""
from dataclasses import dataclass
from math import isfinite
from model import annuity_payment

@dataclass(frozen=True)
class PublicPolicyAssumptions:
    restriction_years: int = 30
    public_discount_rate_pct: float = 5.0
    target_ami_pct: int = 60

def loan_pv_support(principal, rate_pct, years, discount_pct):
    """Face principal less PV of scheduled fully-amortizing repayments, at public discount rate.
    Positive is a concession; negative means repayments have higher PV than disbursement.
    Does not price credit/default risk, servicing, timing delays, or fees.
    """
    if principal < 0 or rate_pct < 0 or years <= 0 or discount_pct < 0:
        raise ValueError('Invalid public loan assumptions')
    if principal == 0:return 0.0
    payment=annuity_payment(principal,rate_pct,years)
    d=discount_pct/100
    pv=payment*years if d == 0 else payment*(1-(1+d)**(-years))/d
    return principal-pv

def evaluate(p,r,a=PublicPolicyAssumptions()):
    if a.restriction_years < 1 or a.restriction_years > 99 or not 0 <= a.public_discount_rate_pct <= 25:
        raise ValueError('Invalid restriction period / discount rate')
    if not 0<=a.target_ami_pct<=100:raise ValueError('Invalid target AMI')
    homes=r['restricted_units']
    unit_years=homes*a.restriction_years
    loan_concession=loan_pv_support(r['loan'],p.loan_rate_pct,p.loan_years,a.public_discount_rate_pct)
    grant=r['grant']; land=r['land_credit']
    total_pv=grant+land+loan_concession
    return {'restricted_homes':homes,'restricted_unit_years':unit_years,
        'restriction_years':a.restriction_years,'nominal_public_capital':grant+r['loan']+land,
        'grant':grant,'land_contribution_value':land,'loan_face':r['loan'],
        'loan_pv_concession':loan_concession,'net_public_support_pv':total_pv,
        'support_pv_per_restricted_home':total_pv/homes if homes else None,
        'support_pv_per_restricted_unit_year':total_pv/unit_years if unit_years else None,
        'grant_per_restricted_home':grant/homes if homes else None,
        'target_ami_pct':a.target_ami_pct,
        'affordable_at_target_ami':None,
        'cautions': ['Unit-years assume all restricted apartments remain restricted for the full period; not a legal covenant review.',
        'Land contribution is valued at assumed cost reduction, not independent appraisal.',
        'Loan PV captures concessional interest only; not default risk, subsidies for operations, tax exemptions, or administrative costs.',
        'Target AMI is a policy label only: the model has one affordable rent and no unit-level regulatory rent verification.']}
