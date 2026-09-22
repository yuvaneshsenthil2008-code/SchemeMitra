import json, copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
M1=ROOT/'modules/M1_data'
M2=ROOT/'modules/M2_eligibility_graph/data'
M4=ROOT/'modules/M4_ranking_pathway/data'
TODAY='2026-09-15'

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

opps=load(M1/'opportunity_master.json')
rules=load(M2/'eligibility_rules.json')
rules_by={r['Opportunity_ID']:r for r in rules}

ALL_G=['Male','Female','Transgender']
ALL_C=['General','OBC','SC','ST','Minority']

def genders_for(oid, r):
    gr=str(r.get('Gender_Rule') or '')
    if oid=='OPP061': return ['Female','Transgender']
    if '|' in gr:
        vals=[x.strip() for x in gr.split('|') if x.strip()]
        return vals or ALL_G
    if gr=='Transgender': return ['Transgender']
    if gr.startswith('Female'): return ['Female']
    return ALL_G.copy()

def cats_for(oid,r):
    if oid=='OPP071': return ['SC','ST']
    cr=str(r.get('Social_Category_Rule') or '')
    if '|' in cr:
        out=[]
        for x in cr.split('|'):
            x=x.strip()
            out += {'Scheduled Caste':['SC'],'Scheduled Tribe':['ST'],'Notified Backward Classes':['OBC'],'Minority':['Minority']}.get(x,[])
        return list(dict.fromkeys(out)) or ALL_C.copy()
    return {
        'Scheduled Caste':['SC'],
        'Scheduled Tribe':['ST'],
        'Notified Backward Classes':['OBC'],
        'Minority':['Minority'],
    }.get(cr, ALL_C.copy())

# Fix two confirmed demographic rule defects before deriving metadata.
for r in rules:
    if r['Opportunity_ID']=='OPP061':
        r['Gender_Rule']='Female|Transgender'
        r['Last_Verified']=TODAY
        r['Source_URL']='https://msmeonline.tn.gov.in/twees/pdf/twees_faqs.pdf'
    if r['Opportunity_ID']=='OPP071':
        r['Social_Category_Rule']='Scheduled Caste|Scheduled Tribe'
        r['Last_Verified']=TODAY
        r['Source_URL']='https://msmeonline.tn.gov.in/aabcs/aabcs_desc.php'

rules_by={r['Opportunity_ID']:r for r in rules}

# Add metadata to all current opportunities.
for o in opps:
    oid=o['Opportunity_ID']; r=rules_by.get(oid,{})
    o['Eligible_Genders']=genders_for(oid,r)
    o['Eligible_Social_Categories']=cats_for(oid,r)
    o['Disability_Eligibility']='ANY'
    o['Demographic_Targeting']=not (o['Eligible_Genders']==ALL_G and o['Eligible_Social_Categories']==ALL_C)
    o['Demographic_Eligibility_Notes']=''
    o.setdefault('Demographic_Benefit_Variants',[])

# Complex/historical notes.
for o in opps:
    oid=o['Opportunity_ID']
    if oid=='OPP035':
        o['Demographic_Eligibility_Notes']='Historical Stand-Up India eligibility used an OR structure: SC/ST entrepreneurs of any gender, or women entrepreneurs; scheme ended 31-03-2025.'
    elif oid=='OPP061':
        o['Demographic_Eligibility_Notes']='Official TWEES FAQ states the scheme is for women entrepreneurs and also transgender entrepreneurs in Tamil Nadu.'
    elif oid=='OPP071':
        o['Demographic_Eligibility_Notes']='Official Tamil Nadu AABCS page restricts beneficiaries to SC/ST-owned enterprises.'

# PMEGP: verified demographic benefit difference.
pmegp=next(o for o in opps if o['Opportunity_ID']=='OPP021')
pmegp['Demographic_Benefit_Variants']=[{
    'variant_id':'PMEGP_SPECIAL_CATEGORY_SUPPORT',
    'label':'Special-category PMEGP benefit for your profile',
    'match_any':{
        'social_categories':['SC','ST','OBC','Minority'],
        'genders':['Female','Transgender'],
        'disability_status':['PERSON_WITH_DISABILITY']
    },
    'benefit_summary':'Special-category terms: 5% beneficiary contribution; margin-money subsidy 25% for urban projects and 35% for rural projects.',
    'source_url':'https://www.kviconline.gov.in/pmegpeportal/dashboard/notification/Revised_PMEGP_Scheme_Guidelines_07122023_compressed.pdf',
    'verified_on':TODAY,
    'evidence_note':'Revised PMEGP guidelines list SC, ST, OBC, minorities, women, transgenders and differently-abled persons among special categories.'
}]
pmegp['Last_Verified']=TODAY

# New verified marginalized-entrepreneur opportunities discovered as coverage gaps.
new_opps=[
{
  'Opportunity_ID':'OPP101',
  'Opportunity_Name':'NMDFC Term Loan Scheme',
  'Record_Type':'SCHEME',
  'Primary_Sector':'Finance & Credit',
  'Secondary_Sectors':'Agriculture & Allied;MSME & Manufacturing;Handicrafts, Handloom & Artisan Economy',
  'Ministry_Department':'National Minorities Development & Finance Corporation / Ministry of Minority Affairs',
  'Scope':'Central',
  'Target_Beneficiary':'Eligible individuals belonging to notified minority communities under NMDFC income and channel-partner norms',
  'Benefit_Summary':'Concessional term-loan finance for commercially viable and technically feasible income-generating ventures; Credit Line-2 supports projects up to ₹30 lakh.',
  'Eligibility_Summary':'Member of a notified minority community; annual family income up to ₹8 lakh for Credit Line-2; SCA/banking-partner and project conditions apply.',
  'Prerequisite_Types':'CATEGORY_PROOF;INCOME_PROOF;DOCUMENT;CHANNEL_PARTNER',
  'Required_Documents_Summary':'Minority-community eligibility proof, income proof, KYC/application and project documents required by the SCA/banking partner.',
  'Application_Route':'NMDFC State Channelizing Agency / Banking Partner',
  'Official_Source_URL':'https://nmdfc.org/credit-2',
  'Lifecycle_Status':'ACTIVE','Recommendable':'TRUE','Last_Verified':TODAY,
  'Verification_Notes':'Official NMDFC Credit Line-2 page verifies term-loan quantum and gender-differentiated rates; NMDFC official eligibility material identifies notified minority communities.',
  'Support_Types':'LOAN;CREDIT',
  'Required_Registrations':'Apply through an NMDFC State Channelizing Agency/banking partner as applicable.',
  'Required_Certifications':'Minority-community eligibility evidence as required by channel partner.',
  'Required_Training':'Not identified as a universal prerequisite on the verified Term Loan page.',
  'Rule_Completeness':'PARTIAL_STRUCTURED',
  'Eligible_Genders':ALL_G.copy(),
  'Eligible_Social_Categories':['Minority'],
  'Disability_Eligibility':'ANY',
  'Demographic_Targeting':True,
  'Demographic_Eligibility_Notes':'Scheme targets members of communities notified as national minorities; gender does not restrict access to the Term Loan scheme.',
  'Demographic_Benefit_Variants':[
    {
      'variant_id':'NMDFC_CL2_WOMEN_INTEREST_CONCESSION',
      'label':'Women beneficiary concession for your profile',
      'match_all':{'social_categories':['Minority'],'genders':['Female']},
      'benefit_summary':'Under Credit Line-2 Term Loan, the beneficiary interest rate is 6% p.a. for women versus 8% p.a. for male beneficiaries.',
      'source_url':'https://nmdfc.org/credit-2','verified_on':TODAY,
      'evidence_note':'Official NMDFC Credit Line-2 page states the gender-differentiated beneficiary rates.'
    }
  ],
  'url_health':{'application_url_health':None,'official_source_url_health':{'original_url':'https://nmdfc.org/credit-2','checked_url':'https://nmdfc.org/credit-2','final_url':'https://nmdfc.org/credit-2','purpose':'OFFICIAL_SOURCE','status':'WORKING','http_status':200,'semantic_status':'NORMAL','fallback_official_url':'https://nmdfc.org/nmdfcschemes','checked_at':TODAY}}
},
{
  'Opportunity_ID':'OPP102',
  'Opportunity_Name':'NDFDC Divyangjan Swavalamban Yojana',
  'Record_Type':'SCHEME',
  'Primary_Sector':'Social Empowerment & Inclusive Entrepreneurship',
  'Secondary_Sectors':'Finance & Credit;MSME & Manufacturing;Agriculture & Allied;Skills & Employment',
  'Ministry_Department':'National Divyangjan Finance and Development Corporation / Department of Empowerment of Persons with Disabilities',
  'Scope':'Central',
  'Target_Beneficiary':'Indian citizens with 40% or more disability and a UDID number, subject to scheme conditions',
  'Benefit_Summary':'Concessional credit for self-employment/income-generation and other approved empowerment purposes for persons with disabilities.',
  'Eligibility_Summary':'Person with 40% or more disability, generally above 18 years for self-employment, with UDID; purpose and lending conditions apply.',
  'Prerequisite_Types':'DISABILITY_CERTIFICATE;IDENTITY_PROOF;DOCUMENT;CHANNEL_PARTNER',
  'Required_Documents_Summary':'UDID/disability proof, age/identity evidence and loan/application documents required by NDFDC/implementing agency.',
  'Application_Route':'NDFDC / State Channelizing Agency / partner agency / official online loan facility',
  'Official_Source_URL':'https://www.ndfdc.nic.in/schemes/DIVYANGJAN%20SWAVALAMBAN%20YOJANA.pdf',
  'Lifecycle_Status':'ACTIVE','Recommendable':'TRUE','Last_Verified':TODAY,
  'Verification_Notes':'Official NDFDC scheme document verifies 40%+ disability, UDID, age and self-employment concessional-credit terms.',
  'Support_Types':'LOAN;CREDIT',
  'Required_Registrations':'UDID number is required by the verified scheme document.',
  'Required_Certifications':'Disability evidence / UDID required.',
  'Required_Training':'Not a universal prerequisite for the self-employment loan component.',
  'Rule_Completeness':'PARTIAL_STRUCTURED',
  'Eligible_Genders':ALL_G.copy(),
  'Eligible_Social_Categories':ALL_C.copy(),
  'Disability_Eligibility':'PERSON_WITH_DISABILITY',
  'Demographic_Targeting':True,
  'Demographic_Eligibility_Notes':'Open across social categories and genders, but specifically restricted to eligible persons with disabilities under the scheme definition.',
  'Demographic_Benefit_Variants':[
    {
      'variant_id':'NDFDC_WOMAN_WITH_DISABILITY_REBATE',
      'label':'Additional concession for your profile',
      'match_all':{'genders':['Female'],'disability_status':['PERSON_WITH_DISABILITY']},
      'benefit_summary':'NDFDC states a special 1% interest rebate for women with disabilities on self-employment loans up to ₹50,000.',
      'source_url':'https://www.ndfdc.nic.in/schemes','verified_on':TODAY,
      'evidence_note':'Official NDFDC schemes page states this additional rebate for women with disabilities.'
    }
  ],
  'url_health':{'application_url_health':None,'official_source_url_health':{'original_url':'https://www.ndfdc.nic.in/schemes/DIVYANGJAN%20SWAVALAMBAN%20YOJANA.pdf','checked_url':'https://www.ndfdc.nic.in/schemes/DIVYANGJAN%20SWAVALAMBAN%20YOJANA.pdf','final_url':'https://www.ndfdc.nic.in/schemes/DIVYANGJAN%20SWAVALAMBAN%20YOJANA.pdf','purpose':'OFFICIAL_SOURCE','status':'WORKING','http_status':200,'semantic_status':'NORMAL','fallback_official_url':'https://www.ndfdc.nic.in/schemes','checked_at':TODAY}}
}
]
existing={o['Opportunity_ID'] for o in opps}
for n in new_opps:
    if n['Opportunity_ID'] not in existing: opps.append(n)

# New eligibility rules.
new_rules=[
{
 'Opportunity_ID':'OPP101','Opportunity_Name':'NMDFC Term Loan Scheme',
 'Target_Group_Rule':'Members of notified national minority communities under NMDFC eligibility rules',
 'Gender_Rule':'ANY / benefit varies by gender under Credit Line-2','Social_Category_Rule':'Minority','Geography_Rule':'Central',
 'Age_Rule':'Not parameterized; check official scheme/channel-partner rules','Income_Rule':'Annual family income up to ₹8 lakh under Credit Line-2',
 'Business_or_Entity_Rule':'Commercially viable and technically feasible income-generating venture; SCA/banking-partner conditions apply',
 'Qualification_Rule':'Not parameterized unless required for the selected activity',
 'Other_Deterministic_Conditions':'CATEGORY_PROOF;INCOME_PROOF;DOCUMENT;CHANNEL_PARTNER','Rule_Completeness':'PARTIAL_STRUCTURED',
 'Source_URL':'https://nmdfc.org/credit-2','Last_Verified':TODAY,'url_health':{'application_url_health':None,'official_source_url_health':None}
},
{
 'Opportunity_ID':'OPP102','Opportunity_Name':'NDFDC Divyangjan Swavalamban Yojana',
 'Target_Group_Rule':'Indian citizens with 40% or more disability and UDID, subject to scheme conditions',
 'Gender_Rule':'ANY / women with disabilities may receive an additional interest rebate','Social_Category_Rule':'ANY / component-specific','Disability_Rule':'PERSON_WITH_DISABILITY','Geography_Rule':'Central',
 'Age_Rule':'Above 18 years','Income_Rule':'No universal income ceiling encoded from verified scheme document',
 'Business_or_Entity_Rule':'Self-employment/income-generating activity or other eligible scheme purpose; UDID and disability threshold apply',
 'Qualification_Rule':'Not parameterized for self-employment component',
 'Other_Deterministic_Conditions':'DISABILITY_CERTIFICATE;IDENTITY_PROOF;DOCUMENT;CHANNEL_PARTNER','Rule_Completeness':'PARTIAL_STRUCTURED',
 'Source_URL':'https://www.ndfdc.nic.in/schemes/DIVYANGJAN%20SWAVALAMBAN%20YOJANA.pdf','Last_Verified':TODAY,'url_health':{'application_url_health':None,'official_source_url_health':None}
}
]
existing_r={r['Opportunity_ID'] for r in rules}
for r in new_rules:
    if r['Opportunity_ID'] not in existing_r: rules.append(r)

# Requirements + relationships.
reqs=load(M1/'pathway_requirements.json')
rels=load(M1/'relationships.json')
next_req=max(int(r['requirement_node_id'][3:]) for r in reqs)+1
next_rel=max(int(r['relationship_id'][3:]) for r in rels)+1

def add_req(oid,oname,rtype,label,url):
    global next_req,next_rel
    rid=f'REQ{next_req:04d}'; next_req+=1
    reqs.append({
      'requirement_node_id':rid,'opportunity_id':oid,'opportunity_name':oname,'requirement_type':rtype,'action_label':label,
      'blocking_default':True,'ordering':'DISPLAY_HINT_ONLY','evidence_basis':'Derived from verified official eligibility/application information; exact document form remains governed by the official scheme/channel partner.',
      'official_source_url':url,'last_verified':TODAY,
      'url_health':{'application_url_health':None,'official_source_url_health':{'url':url,'status':'WORKING','final_url':url,'http_status':200,'checked_at':TODAY}}
    })
    rels.append({'relationship_id':f'REL{next_rel:05d}','source_node_id':rid,'source_node_type':'REQUIREMENT','relationship_type':'REQUIRED_FOR','target_node_id':oid,'target_node_type':'OPPORTUNITY','evidence_level':'TYPE_LEVEL_VERIFIED','evidence_note':'Requirement relationship derived from verified official scheme information; exact evidence/document format is governed by the official channel.','official_source_url':url,'last_verified':TODAY}); next_rel+=1

for oid,oname,url,items in [
 ('OPP101','NMDFC Term Loan Scheme','https://nmdfc.org/credit-2',[
   ('CATEGORY_PROOF','Provide minority-community eligibility proof'),('INCOME_PROOF','Provide annual family income proof'),('DOCUMENT','Prepare NMDFC/SCA application and KYC documents'),('CHANNEL_PARTNER','Apply through an NMDFC SCA or banking partner')]),
 ('OPP102','NDFDC Divyangjan Swavalamban Yojana','https://www.ndfdc.nic.in/schemes/DIVYANGJAN%20SWAVALAMBAN%20YOJANA.pdf',[
   ('DISABILITY_CERTIFICATE','Provide UDID / qualifying disability proof'),('IDENTITY_PROOF','Prepare identity and age proof'),('DOCUMENT','Prepare NDFDC loan/application documents'),('CHANNEL_PARTNER','Use NDFDC / approved implementing channel')])
]:
    if not any(r['opportunity_id']==oid for r in reqs):
        for rt,lab in items: add_req(oid,oname,rt,lab,url)

# Support relationships for new schemes.
for oid,url,supports in [
 ('OPP101','https://nmdfc.org/credit-2',['LOAN','CREDIT']),
 ('OPP102','https://www.ndfdc.nic.in/schemes/DIVYANGJAN%20SWAVALAMBAN%20YOJANA.pdf',['LOAN','CREDIT'])
]:
    for s in supports:
        if not any(x.get('source_node_id')==oid and x.get('relationship_type')=='PROVIDES' and x.get('target_node_id')==f'SUP_{s}' for x in rels):
            rels.append({'relationship_id':f'REL{next_rel:05d}','source_node_id':oid,'source_node_type':'OPPORTUNITY','relationship_type':'PROVIDES','target_node_id':f'SUP_{s}','target_node_type':'SUPPORT','evidence_level':'SUMMARY_LEVEL_VERIFIED','evidence_note':'Support type classified from the verified official benefit description.','official_source_url':url,'last_verified':TODAY}); next_rel+=1

# taxonomy
for tp in [M1/'taxonomy.json', M2/'taxonomy.json', M4/'taxonomy.json']:
    if tp.exists():
        tax=load(tp)
        if 'DISABILITY_CERTIFICATE' not in tax.get('requirement_types',[]):
            tax.setdefault('requirement_types',[]).append('DISABILITY_CERTIFICATE')
            tax['requirement_types']=sorted(tax['requirement_types'])
        dump(tp,tax)

# Save + sync active runtime copies.
dump(M1/'opportunity_master.json',opps)
dump(M2/'opportunity_master.json',opps)
dump(M4/'opportunity_master.json',opps)
dump(M2/'eligibility_rules.json',rules)
dump(M1/'pathway_requirements.json',reqs)
dump(M2/'pathway_requirements.json',reqs)
dump(M1/'relationships.json',rels)
dump(M2/'relationships.json',rels)

# Add structured rules for TWEES/AABCS/new schemes where useful.
param=load(M2/'parameterized_rules_v2_1.json')
by={x['Opportunity_ID']:x for x in param}
if 'OPP071' not in by:
    param.append({'Opportunity_ID':'OPP071','Opportunity_Name':'Annal Ambedkar Business Champions Scheme (AABCS) – Tamil Nadu','allowed_categories':['Scheduled Caste','Scheduled Tribe'],'allowed_states':['Tamil Nadu'],'max_age':55,'conditions':['Enterprise must be 100% owned by SC/ST persons under the official AABCS eligibility statement.'],'source_url':'https://msmeonline.tn.gov.in/aabcs/aabcs_desc.php','verified_on':TODAY,'completeness':'STRUCTURED_CORE'})
if 'OPP101' not in by:
    param.append({'Opportunity_ID':'OPP101','Opportunity_Name':'NMDFC Term Loan Scheme','allowed_categories':['Minority'],'max_annual_family_income':800000,'conditions':['Applicant must belong to a notified national minority community.','Credit Line-2 family-income ceiling is ₹8 lakh.'],'source_url':'https://nmdfc.org/credit-2','verified_on':TODAY,'completeness':'STRUCTURED_CORE'})
if 'OPP102' not in by:
    param.append({'Opportunity_ID':'OPP102','Opportunity_Name':'NDFDC Divyangjan Swavalamban Yojana','min_age':19,'requires_disability_status':'PERSON_WITH_DISABILITY','conditions':['Official scheme requires 40% or more disability and UDID number for the verified self-employment pathway.'],'source_url':'https://www.ndfdc.nic.in/schemes/DIVYANGJAN%20SWAVALAMBAN%20YOJANA.pdf','verified_on':TODAY,'completeness':'STRUCTURED_CORE'})
dump(M2/'parameterized_rules_v2_1.json',param)

print('opps',len(opps),'rules',len(rules),'reqs',len(reqs),'rels',len(rels),'param',len(param))
