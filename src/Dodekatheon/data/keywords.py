def has_keyword(unit, category, keyword):
    """
    unit: a Unit instance
    category: 'unit' or 'faction'
    keyword: string to test (case-insensitive)
    """
    kws = unit.datasheet.get('keywords',{}).get(category,[])
    return any(k.lower() == keyword.lower() for k in kws)


def can_attach_to_army(subject, army_faction):
    
    # subject may be a Unit or a raw datasheet dict
    kws = (subject.datasheet if hasattr(subject,'datasheet') else subject)
    return army_faction in kws['keywords']['faction']

def ignores_terrain(unit):
    return 'Fly' in unit.datasheet['keywords']['unit']

def benefits_from_cover(unit):
    return 'Infantry' in unit.datasheet['keywords']['unit']