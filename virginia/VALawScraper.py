import requests
import json
import urllib3
import os
from datetime import datetime
from jsonpath_ng import jsonpath, parse

# Suppress only the single InsecureRequestWarning from urllib3 needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = 'https://law.lis.virginia.gov/api/'

def fetch_data(url):
    try:
        print(f"Retrieving: {url}")
        response = requests.get(url, verify=False)  # Bypass SSL verification
        response.raise_for_status()
        try:
            return response.json()
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from {url}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return None

def gather_administrative_code():
    
    ''' API responses of JSON schema
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "RegulationSchema",
        "type": "object",
        "properties": {
            "TitleNumber": {
                "type": "string"
            },
            "TitleName": {
                "type": "string"
            },
            "AgencyList": {
                "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "AgencyNumber": {
                        "type": "string"
                    },
                "AgencyName": {
                    "type": "string"
                },
                "Preface": {
                    "type": "object",
                    "properties": {
                        "Preface": {
                            "type": "string"
                        },
                        "PrefaceSummary": {
                            "type": "string"
                        }
                    },
                    "required": ["Preface", "PrefaceSummary"]
                },
                "ChapterList": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ChapterNumber": {
                                "type": "string"
                            },
                            "ChapterName": {
                                "type": "string"
                            },
                            "Sections": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "PartNumber": {
                                            "type": "string"
                                        },
                                        "PartName": {
                                            "type": "string"
                                        },
                                        "ArticleNumber": {
                                            "type": "string"
                                        },
                                        "ArticleName": {
                                            "type": "string"
                                        },
                                        "SectionNumber": {
                                            "type": "string"
                                        },
                                        "SectionTitle": {
                                            "type": "string"
                                        },
                                        "Body": {
                                            "type": "string"
                                        },
                                        "Authority": {
                                            "type": "string"
                                        },
                                        "HistoricalNote": {
                                            "type": "string"
                                        }
                                    },
                                    "required": ["PartNumber", "PartName", "SectionNumber", "SectionTitle", "Body"]
                                }
                            },
                            "required": ["ChapterNumber", "ChapterName", "Sections"]
                        }
                    }
                },
                "required": ["AgencyNumber", "AgencyName", "Preface", "ChapterList"]
                }
            }
        },
        "required": ["TitleNumber", "TitleName", "AgencyList"]
    }
    '''
    # jsonpath expressions to extract data from JSON response with schema above
    jsonpath_expressions = {
        "TitleNumber": parse('$.TitleNumber'),
        "TitleName": parse('$.TitleName'),
        "AgencyList": parse('$.AgencyList[*]'),
        "AgencyNumber": parse('$.AgencyList[*].AgencyNumber'),
        "AgencyName": parse('$.AgencyList[*].AgencyName'),
        "Preface": parse('$.AgencyList[*].Preface'),
        "PrefaceText": parse('$.AgencyList[*].Preface.Preface'),
        "PrefaceSummary": parse('$.AgencyList[*].Preface.PrefaceSummary'),
        "ChapterList": parse('$.AgencyList[*].ChapterList[*]'),
        "ChapterNumber": parse('$.AgencyList[*].ChapterList[*].ChapterNumber'),
        "ChapterName": parse('$.AgencyList[*].ChapterList[*].ChapterName'),
        "Sections": parse('$.AgencyList[*].ChapterList[*].Sections[*]'),
        "PartNumber": parse('$.AgencyList[*].ChapterList[*].Sections[*].PartNumber'),
        "PartName": parse('$.AgencyList[*].ChapterList[*].Sections[*].PartName'),
        "ArticleNumber": parse('$.AgencyList[*].ChapterList[*].Sections[*].ArticleNumber'),
        "ArticleName": parse('$.AgencyList[*].ChapterList[*].Sections[*].ArticleName'),
        "SectionNumber": parse('$.AgencyList[*].ChapterList[*].Sections[*].SectionNumber'),
        "SectionTitle": parse('$.AgencyList[*].ChapterList[*].Sections[*].SectionTitle'),
        "Body": parse('$.AgencyList[*].ChapterList[*].Sections[*].Body'),
        "Authority": parse('$.AgencyList[*].ChapterList[*].Sections[*].Authority'),
        "HistoricalNote": parse('$.AgencyList[*].ChapterList[*].Sections[*].HistoricalNote')
    }
    

    # Administrative Code Data
    titles = fetch_data(BASE_URL + "AdministrativeCodeGetTitleListOfJson")
    if titles is not None:
        for title in titles:
            title_number = title["TitleNumber"]
            title_name = title["TitleName"]
            agencies_fetched = fetch_data(BASE_URL + f"AdministrativeCodeGetAgencyListOfJson/{title_number}")
            if agencies_fetched is not None:
                agencies = agencies_fetched.get("AgencyList", [])
                for agency in agencies:
                    agency_number = agency["AgencyNumber"]
                    preface = fetch_data(BASE_URL + f"AdministrativeCodePrefaceJson/{title_number}/{agency_number}")
                    if preface is not None:
                        preface.pop("TitleNumber", None)
                        preface.pop("AgencyNumber", None)
                        preface.pop("TitleName", None)
                        preface.pop("AgencyName", None)
                        agency.update({"Preface": preface})
                        #all_data.setdefault("AdministrativeCodePrefaceJson", {})[f"{title_number}_{agency_number}"] = preface

                    chapters_obj = fetch_data(BASE_URL + f"AdministrativeCodeChapterListOfJson/{title_number}/{agency_number}")
                    if chapters_obj is not None:
                        jsonpath_expression = parse('$.AgencyList')
                        matches = jsonpath_expression.find(chapters_obj)
                        #all_data.setdefault("AdministrativeCodeChapterListOfJson", {})[f"{title_number}_{agency_number}"] = chapters
                        for agency_fetched in chapters_obj["AgencyList"]:
                            if agency_fetched["AgencyNumber"] == agency_number:
                                agency_fetched.pop("AgencyNumber", None)
                                agency_fetched.pop("AgencyName", None)
                                chapter_list = agency_fetched["ChapterList"]
                                for chapter in chapter_list:
                                    chapter_number = chapter["ChapterNumber"]
                                    sections_obj = fetch_data(BASE_URL + f"AdministrativeCodeGetSectionListOfJson/{title_number}/{agency_number}/{chapter_number}")
                                    if sections_obj is not None:
                                        #use jsonpath to extract "Sections" data from JSON response with schema above.
                                        sections_matches = jsonpath_expressions["Sections"].find(sections_obj)
                                        # Use the JSONPath expression to find and extract sections data
                                        sections = [match.value for match in sections_matches]
                                        chapter["Sections"] = sections
                                        for section in sections:
                                            section_number = section["SectionNumber"]

                                            '''	
                                            This service returns a the Administratve Section detail by 'titleNumber', 'agencyNumber', 'chapterNumber', 'sectionNumber', 'sectionNumberPoint', 'sectionNumberColon' (if no point or colon, pass a 0 for each value)
                                            but there is no refernce to the API calls for how to get 'sectionNumberPoint', 'sectionNumberColon' so we are using zeros as a placeholder for now.
                                            '''
                                            
                                            sectionNumberPoint = 0
                                            sectionNumberColon = 0
                                                                              
                                            section_details_obj =  fetch_data(BASE_URL + f"AdministrativeCodeGetSectionDetailsJson/{title_number}/{agency_number}/{chapter_number}/{section_number}/{sectionNumberPoint}/{sectionNumberColon}")
                                            if section_details_obj is not None:
                                                #use jsonpath to extract "Body" data from JSON response with schema above
                                                section_detail_matches = jsonpath_expressions["Body"].find(section_details_obj)
                                                # Use the JSONPath expression to find and extract section detail data
                                                section_detail = [match.value for match in section_detail_matches]
                                                section["Body"] = section_detail[0]
                                    chapter.update({"Sections":sections})   
                    agency.update({"ChapterList":chapter_list}) 
            title.update({"AgencyList":agencies})
    return titles
    
def gather_authorities_data():
    # dict to hold all data in new schema
    authorities = []
    # Authorities Data
    authorities = fetch_data(BASE_URL + "AuthoritiesGetListOfJson")
    if authorities is not None:
        for authority in authorities:
            short_name = authority.get("ShortName")
            if short_name:
                authority_detail = fetch_data(BASE_URL + f"AuthoritiesGetDetailJson/{short_name}")
                if authority_detail is not None:
                    authority["Body"] = authority_detail["Body"]
    return authorities

def gather_charters_data():
    # Charters Data
    charters = []
    charters = fetch_data(BASE_URL + "ChartersGetListOfJson")
    if charters is not None:
        for charter in charters:
            short_name = charter.get("ShortName")
            if short_name:
                charter_detail = fetch_data(BASE_URL + f"ChartersGetDetailJson/{short_name}")
                if charter_detail is not None:
                    charter["Body"] = charter_detail["Body"]
    return charters

def gather_statute_data():
    all_data ={}
    # Code of Virginia Data
    titles = fetch_data(BASE_URL + "CoVTitlesGetListOfJson")
    if titles is not None:
        all_data["CoVTitlesGetListOfJson"] = titles

        for title in titles:
            title_number = title["TitleNumber"]
            chapters = fetch_data(BASE_URL + f"CoVChaptersGetListOfJson/{title_number}")
            if chapters is not None:
                all_data.setdefault("CoVChaptersGetListOfJson", {})[title_number] = chapters

                for chapter in chapters.get("ChapterList", []):
                    chapter_number = chapter.get("ChapterNum")
                    if chapter_number:
                        sections = fetch_data(BASE_URL + f"CoVSectionsGetListOfJson/{title_number}/{chapter_number}")
                        if sections is not None:
                            all_data.setdefault("CoVSectionsGetListOfJson", {})[f"{title_number}_{chapter_number}"] = sections
                            for article in sections["ArticleList"]:
                                for subpart in article["SubPartList"]:
                                    for section in subpart["SectionList"]:
                                        print(section)
                                        section_number = section.get("SectionNumber")
                                        if section_number:
                                            section_details = fetch_data(BASE_URL + f"CoVSectionsGetSectionDetailsJson/{section_number}")
                                            if section_details is not None:
                                                all_data.setdefault("CoVSectionsGetSectionDetailsJson", {})[section_number] = section_details
                                print(section)
    return all_data
def gather_compacts_data():
    # Compacts Data
    all_data ={}
    compacts = fetch_data(BASE_URL + "CompactsTitlesGetListOfJson")
    if compacts is not None:
        all_data["CompactsGetListOfJson"] = compacts

        for compact in compacts:
            short_name = compact.get("ShortName")
            if short_name:
                compact_detail = fetch_data(BASE_URL + f"CompactSectionsGetSectionDetailsJson/{short_name}")
                if compact_detail is not None:
                    all_data.setdefault("CompactSectionsGetSectionDetailsJson", {})[short_name] = compact_detail
    return all_data

    # Constitution Data
def gather_constitution_data():
    all_data ={}
    articles = fetch_data(BASE_URL + "ConstitutionArticlesGetListOfJson")
    if articles is not None:
        all_data["ConstitutionArticlesGetListOfJson"] = articles

        for article in articles:
            article_number = article.get("ArticleNumber")
            if article_number:
                sections = fetch_data(BASE_URL + f"ConstitutionSectionsGetListOfJson/{article_number}")
                if sections is not None:
                    all_data.setdefault("ConstitutionSectionsGetListOfJson", {})[article_number] = sections

                    for section in sections.get("Sections", []):
                        section_number = section.get("SectionNumber")
                        if section_number:
                            section_details = fetch_data(BASE_URL + f"ConstitutionSectionDetailsJson/{article_number}/{section_number}")
                            if section_details is not None:
                                all_data.setdefault("ConstitutionSectionDetailsJson", {})[f"{article_number}_{section_number}"] = section_details
    return all_data

def gather_unified_code_data():
    # Uncodified Acts Data
    all_data ={}
    current_year = datetime.now().year 
    years = list(range(1946, current_year + 1))
    for year in years:
        chapters = fetch_data(BASE_URL + f"UncodifiedActChapterByYearGetListOfJson/{year}")
        if chapters is not None:
            all_data.setdefault("UncodifiedActChapterByYearGetListOfJson", {})[year] = chapters

    return all_data

def save_data_as_per_schema(data, path, filename):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, filename+'.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("All data has been successfully fetched and saved in 'comprehensive_VA_code.json'")

if __name__ == "__main__":
    #Get the path of the current script
    current_script_path = os.path.realpath(__file__)
    # Get the directory of the current script
    current_directory = os.path.dirname(current_script_path)
    # Define the subdirectory name
    subdirectory_name = "json_code_data"
    # Create the path for the subdirectory
    subdirectory_path = os.path.join(current_directory, subdirectory_name)
    
    #gather admin data
    administrative_code = gather_administrative_code()
    filename = "admin_code_data_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data_as_per_schema(administrative_code, subdirectory_path, filename)
    
    #gather the authorities data
    authorities_data = gather_authorities_data()
    filename = "authorities_data_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data_as_per_schema(authorities_data, subdirectory_path, filename)
    
    #gather charters data
    charters_data = gather_charters_data()
    filename = "charters_data_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data_as_per_schema(charters_data, subdirectory_path, filename)
    
    #gather statute data
    statute_data = gather_statute_data()
    filename = "statute_data_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data_as_per_schema(statute_data, subdirectory_path, filename)
    
    #gather compacts data
    compacts_data = gather_compacts_data()
    filename = "compacts_data_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data_as_per_schema(compacts_data, subdirectory_path, filename)
    
    #gather constitution data
    constitution_data = gather_constitution_data()
    filename = "constitution_data_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data_as_per_schema(constitution_data, subdirectory_path, filename)
    
    #gather unified code data
    unified_code_data = gather_unified_code_data()
    filename = "unified_code_data_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data_as_per_schema(unified_code_data, subdirectory_path, filename)
    
