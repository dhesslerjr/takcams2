import json

def toJSON(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__, 
        sort_keys=True,
        indent=4)

def restOfLineAfter(token,line):
    pos=line.find(token)
    if(pos>-1):
        ret=line[pos+len(token):]
        return ret
    else:
        return ''

     
class UserTip:
    def __init__(self,step_no,raw_ai_text):
        self.parse_ok=True
        self.for_step=step_no
        self.raw=raw_ai_text
        self.conflict=False
        self.tip=""
        self.explanations=[]
		#parse AI raw content here

        #tip
        lines=self.raw.splitlines()
        doing_explanations=False
        for aline in lines:
            aline=aline.strip()
            if(doing_explanations):
                exp=restOfLineAfter('- ',aline)
                if(exp):
                    self.explanations.append(exp)
                else:
                     doing_explanations=False 
            else:
                atip = restOfLineAfter('Tip: ',aline)
                if(atip):
                    self.tip=atip
                if(aline.find('Explanations:')>-1):
                    doing_explanations=True
    
        #done?
        self.parse_ok=(len(self.tip)>0)
        self.conflict=(len(self.explanations)>0)
		
class SystemSuggestion:
	def __init__(self,step_no,raw_ai_text):
		self.for_step=step_no
		self.raw=raw_ai_text
		self.suggestion=""
		self.references=[]
		#parse AI raw content here

class SystemAnswer:
    def __init__(self,step_no,raw_ai_text):
        self.for_step=step_no
        self.raw=raw_ai_text
        self.question=""
        self.confidence_score=0.0
        self.verified=False
        self.answer={
            'key_details': [],
            'technical_notes': [],
            'references': []
        }
		#parse AI raw content here
	
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)

class TakcamsData_v1:

    def __init__(self,contexts,user_name,user_email):
        takcams_schema_version=2
        self.context = []
        for c in contexts:
            self.contexts.append(c)
        self.user = { 'name': user_name, 'email': user_email }
        self.user_input = {}
        self.ai_user_tip={} # type: UserTip
        self.ai_answer = {} # type: SystemAnswer
        self.ai_system_suggestion = {} # type: SystemSuggestion
    
    def set_user_input(self,step_no,tip,question):
        self.user_input = {'current_step':step_no,'tip':tip,'question':question }

    def set_user_tip(self,raw_ai_tip):
        me = UserTip(self.user_input['current_step'],raw_ai_tip)
        self.ai_user_tip = me


    

		
#LLM raw output examples for testing
		
raw_tip_example='''Your tip: a tip for the current step from the user
				 
				=== Results ===
				 
				Tip: a tip for the current step from the user
				 
				Conflicts: Yes there are conflicts
				
				Explanations:
				- the first conflict info
				- the second conflict info
'''

raw_suggestion_example='''Suggestion: Here is a system suggestion for step two.
				References:
				- reference 1
				- reference 2
'''

raw_answer_example='''Your question: how many different particles are there in an atom
				 
				=== Results ===
				 
				Question: how many different particles are there in an atom
				 
				Answer: There are 3 main types of particles found in an atom: protons, neutrons, and electrons.
				 
				Key Details: Protons are positively charged particles found in the nucleus
				- Neutrons have no charge and are also found in the nucleus
				- Electrons are negatively charged particles that orbit the nucleus
				 
				Technical Notes: Atoms can also have other subatomic particles such as quarks and leptons
				- Protons and neutrons are composed of quarks
				- Electrons are elementary particles
				 
				References: 
				- IUPAC Compendium of Chemical Terminology
				- National Institute of Standards and Technology (NIST)
				 
				Confidence Score: 0.98
'''

schema_full_example = '''
	context=[
		{ name: "",
		  content: "",
		  type: "procedure.json | profile | pre-exists |  guidelines | knowledgebase" }
	],
	user: {
		name: "david hessler",
		email: "david.hessler@20visioneers15.com" },
	user_input: {
		current_step: 2,
		tip: "a tip for the current step from the user",
		question: "a question for the current_step from the user" },
	ai_user_tip: {
		for_step: 2,
		raw: "Your tip: a tip for the current step from the user
				 
				=== Results ===
				 
				Tip: a tip for the current step from the user
				 
				Conflicts: Yes there are conflicts
				
				Explanations:
				- the first conflict info
				- the second conflict info",
		conflict: "True", 
		tip: "a tip for the current step from the user",
		explanations: ["the first conflict info","the second conflict info"],
		confidence_score: 0.55
	},
	ai_answer: {
		for_step: 2,
		raw: "Your question: how many different particles are there in an atom
				 
				=== Results ===
				 
				Question: how many different particles are there in an atom
				 
				Answer: There are 3 main types of particles found in an atom: protons, neutrons, and electrons.
				 
				Key Details: Protons are positively charged particles found in the nucleus
				- Neutrons have no charge and are also found in the nucleus
				- Electrons are negatively charged particles that orbit the nucleus
				 
				Technical Notes: Atoms can also have other subatomic particles such as quarks and leptons
				- Protons and neutrons are composed of quarks
				- Electrons are elementary particles
				 
				References: 
				- IUPAC Compendium of Chemical Terminology
				- National Institute of Standards and Technology (NIST)
				 
				Confidence Score: 0.98",
		confidence_score: 0.98,
		question: "how many different particles are there in an atom",
		answer: {
					Key_details: ["Protons are positively charged particles found in the nucleus",
						"Neutrons have no charge and are also found in the nucleus",
						"Electrons are negatively charged particles that orbit the nucleus"],
					Technical_notes: ["Atoms can also have other subatomic particles such as quarks and leptons",
						"Protons and neutrons are composed of quarks",
						"Electrons are elementary particles"],
					References: ["IUPAC Compendium of Chemical Terminology",
						"National Institute of Standards and Technology (NIST)"] 
				}
		},
		verified: "Yes"
	},
	ai_system_suggestion: {
		for_step: 2,
		raw: "Suggestion: Here is a system suggestion for step two.
				References:
				- reference 1
				- reference 2
		",
		suggestion: "Here is a system suggestion for step two.",
		references: ["reference 1","reference 2"]
	}
}
'''
