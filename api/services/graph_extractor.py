import json
import re
import uuid
from typing import List, Dict, Any
from config import settings
from openai import OpenAI
from api.services.text_chunker import Chunk
from api.utils.parse_plaintext import parse_plaintext
from api.schemas import Entity, Relationship, CombinedGraphChunk

graph_relation_prompt = """
-Goal-
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.

-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of the following types: [disease, symptom, diagnosis, drug, treatment, adverse event, clinical outcome, risk factor, comorbidity, biomarker, gene, protein, pathway, mutation, laboratory test, diagnostic test, imaging modality, patient population, demographic group, clinical trial, study, guideline, medical procedure, surgical procedure, pathogen, infection, healthcare organization, clinical measurement, physiological process, organ,viral vector, cell line, experimental model, biological marker]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{{tuple_delimiter}}<entity_name>{{tuple_delimiter}}<entity_type>{{tuple_delimiter}}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: an integer score between 1 to 10, indicating strength of the relationship between the source entity and target entity
Format each relationship as ("relationship"{{tuple_delimiter}}<source_entity>{{tuple_delimiter}}<target_entity>{{tuple_delimiter}}<relationship_description>{{tuple_delimiter}}<relationship_strength>)

3. Return output in The primary language of the provided text is "English." as a single list of all the entities and relationships identified in steps 1 and 2. Use **{{record_delimiter}}** as the list delimiter.

4. If you have to translate into The primary language of the provided text is "English.", just translate the descriptions, nothing else!

5. When finished, output {{completion_delimiter}}.

-Examples-
######################

Example 1:

entity_types: [disease, symptom, diagnosis, drug, treatment, adverse event, clinical outcome, risk factor, comorbidity, biomarker, gene, protein, pathway, mutation, laboratory test, diagnostic test, imaging modality, patient population, demographic group, clinical trial, study, guideline, medical procedure, surgical procedure, pathogen, infection, healthcare organization, clinical measurement, physiological process, organ]
text:
Critical care physicians used an internet-linked handheld computer knowledge access system to obtain medical reference material at the point of care. Four community hospital intensive care units participated in a prospective interventional study. Physicians who used the handheld computer for information access demonstrated significantly improved admission order scores and improved clinical decision making.
------------------------
output:
("entity"{{tuple_delimiter}}CRITICAL CARE PHYSICIANS{{tuple_delimiter}}patient population{{tuple_delimiter}}Critical care physicians who participated in the prospective interventional study and used handheld computers to access medical reference information)
{{record_delimiter}}
("entity"{{tuple_delimiter}}COMMUNITY HOSPITAL INTENSIVE CARE UNITS{{tuple_delimiter}}healthcare organization{{tuple_delimiter}}Community hospital intensive care units participating in the study evaluating handheld computer-based knowledge access)
{{record_delimiter}}
("entity"{{tuple_delimiter}}PROSPECTIVE INTERVENTIONAL STUDY{{tuple_delimiter}}study{{tuple_delimiter}}A prospective study designed to evaluate the feasibility and effectiveness of an internet-linked handheld computer knowledge access system)
{{record_delimiter}}
("entity"{{tuple_delimiter}}MEDICAL REFERENCE MATERIAL{{tuple_delimiter}}guideline{{tuple_delimiter}}Clinical reference information and evidence-based medical content made available to physicians through the handheld computer system)
{{record_delimiter}}
("entity"{{tuple_delimiter}}ADMISSION ORDER SCORE{{tuple_delimiter}}clinical outcome{{tuple_delimiter}}A measure of the quality of physician decision making during simulated patient care scenarios)
{{record_delimiter}}
("entity"{{tuple_delimiter}}CLINICAL DECISION MAKING{{tuple_delimiter}}clinical outcome{{tuple_delimiter}}The quality and effectiveness of clinical management decisions made by physicians)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}CRITICAL CARE PHYSICIANS{{tuple_delimiter}}MEDICAL REFERENCE MATERIAL{{tuple_delimiter}}Critical care physicians accessed medical reference material using the handheld computer system during patient care activities{{tuple_delimiter}}9)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}PROSPECTIVE INTERVENTIONAL STUDY{{tuple_delimiter}}COMMUNITY HOSPITAL INTENSIVE CARE UNITS{{tuple_delimiter}}The prospective interventional study was conducted across multiple community hospital intensive care units{{tuple_delimiter}}10)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}CRITICAL CARE PHYSICIANS{{tuple_delimiter}}ADMISSION ORDER SCORE{{tuple_delimiter}}Physicians using the handheld computer system demonstrated improved admission order scores during simulated clinical scenarios{{tuple_delimiter}}8)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}MEDICAL REFERENCE MATERIAL{{tuple_delimiter}}CLINICAL DECISION MAKING{{tuple_delimiter}}Access to medical reference material was associated with improved clinical decision making{{tuple_delimiter}}9)
{{completion_delimiter}}
#############################


Example 2:

entity_types: [disease, drug, biomarker, clinical outcome]
text:
Patients with type 2 diabetes treated with metformin showed significantly lower HbA1c levels compared with untreated patients. Hypertension was associated with increased risk of stroke.
------------------------
output:
```plaintext
("entity"{{tuple_delimiter}}TYPE 2 DIABETES{{tuple_delimiter}}disease{{tuple_delimiter}}A chronic metabolic disorder characterized by elevated blood glucose levels resulting from impaired insulin action or secretion)
{{record_delimiter}}
("entity"{{tuple_delimiter}}METFORMIN{{tuple_delimiter}}drug{{tuple_delimiter}}A first-line medication commonly used to improve glycemic control in patients with type 2 diabetes)
{{record_delimiter}}
("entity"{{tuple_delimiter}}HBA1C{{tuple_delimiter}}biomarker{{tuple_delimiter}}A laboratory biomarker that reflects average blood glucose levels over the previous two to three months and is used to monitor diabetes management)
{{record_delimiter}}
("entity"{{tuple_delimiter}}HYPERTENSION{{tuple_delimiter}}disease{{tuple_delimiter}}A chronic cardiovascular condition characterized by persistently elevated blood pressure)
{{record_delimiter}}
("entity"{{tuple_delimiter}}STROKE{{tuple_delimiter}}clinical outcome{{tuple_delimiter}}A serious cerebrovascular event resulting from interrupted blood supply to the brain and associated neurological impairment)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}METFORMIN{{tuple_delimiter}}TYPE 2 DIABETES{{tuple_delimiter}}Metformin is administered to patients with type 2 diabetes and is associated with improved glycemic control in this population{{tuple_delimiter}}10)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}HBA1C{{tuple_delimiter}}TYPE 2 DIABETES{{tuple_delimiter}}HbA1c is used to assess and monitor long-term glycemic control in patients with type 2 diabetes{{tuple_delimiter}}9)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}HYPERTENSION{{tuple_delimiter}}STROKE{{tuple_delimiter}}Hypertension is associated with an increased risk of stroke and is an important contributing factor to cerebrovascular disease{{tuple_delimiter}}10)
{{completion_delimiter}}
```
#############################

Example 3:

entity_types: [disease, drug, biomarker, clinical outcome]
text:
Glioblastoma patients treated with lentiviral vector-mediated HSV-1-tk gene therapy showed complete tumor regression on MRI and significantly improved survival compared with controls.
------------------------
output:
```plaintext
("entity"{{tuple_delimiter}}GLIOBLASTOMA{{tuple_delimiter}}disease{{tuple_delimiter}}A highly aggressive and malignant primary brain tumor with poor prognosis)
{{record_delimiter}}
("entity"{{tuple_delimiter}}LENTIVIRAL VECTOR{{tuple_delimiter}}drug{{tuple_delimiter}}A viral vector used for gene delivery in gene therapy applications)
{{record_delimiter}}
("entity"{{tuple_delimiter}}HSV-1-TK GENE THERAPY{{tuple_delimiter}}treatment{{tuple_delimiter}}A suicide gene therapy strategy using herpes simplex virus thymidine kinase to induce tumor cell death)
{{record_delimiter}}
("entity"{{tuple_delimiter}}TUMOR REGRESSION{{tuple_delimiter}}clinical outcome{{tuple_delimiter}}Reduction or disappearance of tumor mass observed on imaging)
{{record_delimiter}}
("entity"{{tuple_delimiter}}SURVIVAL{{tuple_delimiter}}clinical outcome{{tuple_delimiter}}Patient survival outcome used to measure treatment effectiveness)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}HSV-1-TK GENE THERAPY{{tuple_delimiter}}GLIOBLASTOMA{{tuple_delimiter}}Gene therapy was applied to glioblastoma to induce tumor cell death{{tuple_delimiter}}10)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}LENTIVIRAL VECTOR{{tuple_delimiter}}HSV-1-TK GENE THERAPY{{tuple_delimiter}}Lentiviral vectors were used to deliver suicide gene therapy into tumor cells{{tuple_delimiter}}10)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}HSV-1-TK GENE THERAPY{{tuple_delimiter}}TUMOR REGRESSION{{tuple_delimiter}}Gene therapy resulted in complete tumor regression observed on MRI{{tuple_delimiter}}9)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}TUMOR REGRESSION{{tuple_delimiter}}SURVIVAL{{tuple_delimiter}}Tumor regression was associated with improved survival outcomes{{tuple_delimiter}}8)
{{completion_delimiter}}
```
#############################


-Real Data-
######################
entity_types: entity_types: [disease, symptom, diagnosis, drug, treatment, adverse event, clinical outcome, risk factor, comorbidity, biomarker, gene, protein, pathway, mutation, laboratory test, diagnostic test, imaging modality, patient population, demographic group, clinical trial, study, guideline, medical procedure, surgical procedure, pathogen, infection, healthcare organization, clinical measurement, physiological process, organ]
text: {input_text}
######################
output:
"""

class GraphRelationExtractor:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY
        )

    def extract_from_chunk(self, chunk_text: str) -> dict:
        if not chunk_text or not chunk_text.strip():
            return {"raw_output": "", "entities": [], "relationships": []}

        completion = self.client.chat.completions.create(
            model=settings.AZURE_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": graph_relation_prompt},
                {"role": "user", "content": "Your task is to extract entities and relationships from the following text:\n\n" + chunk_text},
            ],
            max_tokens=4096,
            temperature=0,
        )

        content = completion.choices[0].message.content.strip()
        try:
            parsed = parse_plaintext(content)
            return {
                "raw_output": content,
                "entities": parsed.get("entities", []),
                "relationships": parsed.get("relationships", []),
            }
        except (IndexError, ValueError, Exception) as e:
            return {"raw_output": content, "entities": [], "relationships": []}

    def extract_for_chunks(self, chunks: List[Chunk]) -> List[CombinedGraphChunk]:
        results = []
        for chunk in chunks:
            graph_data = self.extract_from_chunk(chunk.content)
            
            results.append(CombinedGraphChunk(
                id=f"{uuid.uuid4()}",
                chunk=chunk,
                entities=[Entity(**e) for e in graph_data["entities"]],
                relationships=[Relationship(**r) for r in graph_data["relationships"]],
                raw_output=graph_data["raw_output"],
                file_name=None
            ))
        return results

    def save_graph_results(self, graph_results: List[CombinedGraphChunk], output_path: str = "chunk_graph.json") -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([res.dict() for res in graph_results], f, ensure_ascii=False, indent=2)