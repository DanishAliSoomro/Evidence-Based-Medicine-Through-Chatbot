import re

def parse_plaintext(raw_text: str) -> dict:
    raw_text = raw_text.replace('\n', '').replace('```plaintext', '').replace('```', '')
    records = re.split(r'\{\{record_delimiter\}\}|\{\{completion_delimiter\}\}', raw_text)

    entities = []
    relationships = []

    for rec in records:
        rec = rec.strip()
        if not rec:
            continue

        # Entity: handle any delimiter variant before description
        m = re.match(
            r'\("entity"\{\{tuple_delimiter\}\}(.+?)\{\{tuple_delimiter\}\}(.+?)\{\{(?:tuple_delimiter|tuple_description|entity_description)\}\}(.+?)\)?\'?$',
            rec
        )
        if m:
            entities.append({
                'name': m.group(1).strip(),
                'type': m.group(2).strip(),
                'description': m.group(3).strip().rstrip(")'")
            })
            continue

        # Relationship
        m = re.match(
            r'\("relationship"\{\{tuple_delimiter\}\}(.+?)\{\{tuple_delimiter\}\}(.+?)\{\{tuple_delimiter\}\}(.+?)\{\{tuple_delimiter\}\}(\d+)\)?$',
            rec
        )
        if m:
            relationships.append({
                'source': m.group(1).strip(),
                'target': m.group(2).strip(),
                'description': m.group(3).strip(),
                'strength': int(m.group(4))
            })

    return {
        'entities': entities,
        'relationships': relationships
    }


if __name__ == "__main__":
    result = parse_plaintext(
        """
("entity"{{tuple_delimiter}}DECENTRALIZED AUTONOMOUS ORGANIZATIONS{{tuple_delimiter}}open-source tool{{tuple_delimiter}}Decentralized autonomous organizations (DAOs) are entities designed to disperse control among participants through decentralized governance mechanisms, often implemented via blockchain technology){{record_delimiter}}\n("entity"{{tuple_delimiter}}DAO GOVERNANCE{{tuple_delimiter}}security measures{{tuple_delimiter}}DAO governance refers to the processes and mechanisms by which decentralized autonomous organizations manage decision-making and control, often involving voting and proposal systems to ensure distributed participation){{record_delimiter}}\n("entity"{{tuple_delimiter}}MONITORING LIMITS{{tuple_delimiter}}security measures{{tuple_delimiter}}Monitoring limits in DAO governance refer to the capacity constraints on participants\' ability to effectively monitor and respond to governance proposals, which can impact decentralization and participation){{record_delimiter}}\n("entity"{{tuple_delimiter}}PROPOSAL FLOW{{tuple_delimiter}}dataset{{tuple_delimiter}}Proposal flow is the rate or volume of governance proposals submitted within a DAO, which affects the workload and participation capacity of voters){{record_delimiter}}\n("entity"{{tuple_delimiter}}ACTIVE VOTERS{{tuple_delimiter}}dataset{{tuple_delimiter}}Active voters are participants in a DAO who engage in voting on governance proposals, whose responsiveness can decline when proposal activity exceeds certain thresholds){{record_delimiter}}\n("entity"{{tuple_delimiter}}VOTING CONCENTRATION{{tuple_delimiter}}evaluation metrics{{tuple_delimiter}}Voting concentration measures the degree to which voting power or participation is concentrated among a small number of participants in DAO governance){{record_delimiter}}\n("entity"{{tuple_delimiter}}KINK MODEL{{tuple_delimiter}}evaluation metrics{{tuple_delimiter}}A kink model is a statistical model used to estimate changes in marginal responsiveness or behavior at certain threshold points, applied here to analyze DAO governance participation){{record_delimiter}}\n("relationship"{{tuple_delimiter}}PROPOSAL FLOW{{tuple_delimiter}}ACTIVE VOTERS{{tuple_delimiter}}Rising proposal flow increases governance workload, which can reduce the marginal responsiveness of active voters once a threshold is crossed{{tuple_delimiter}}8){{record_delimiter}}\n("relationship"{{tuple_delimiter}}MONITORING LIMITS{{tuple_delimiter}}DAO GOVERNANCE{{tuple_delimiter}}Monitoring limits represent capacity constraints that affect the effectiveness of DAO governance by limiting participant engagement{{tuple_delimiter}}7){{record_delimiter}}\n("relationship"{{tuple_delimiter}}KINK MODEL{{tuple_delimiter}}VOTING CONCENTRATION{{tuple_delimiter}}The kink model is used to study voting concentration by identifying thresholds where decentralization gains diminish{{tuple_delimiter}}8){{record_delimiter}}\n("relationship"{{tuple_delimiter}}VOTING CONCENTRATION{{tuple_delimiter}}DAO GOVERNANCE{{tuple_delimiter}}Voting concentration impacts the decentralization and effectiveness of DAO governance mechanisms{{tuple_delimiter}}9){{completion_delimiter}}
        """.strip()
    )

    print(result)
