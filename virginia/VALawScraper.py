import requests
import json
import urllib3
from datetime import datetime

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

def gather_all_data():
    all_data = {}

    # Administrative Code Data
    titles = fetch_data(BASE_URL + "AdministrativeCodeGetTitleListOfJson")
    if titles is not None:
        all_data["AdministrativeCodeGetTitleListOfJson"] = titles

        for title in titles:
            title_number = title["TitleNumber"]
            agencies = fetch_data(BASE_URL + f"AdministrativeCodeGetAgencyListOfJson/{title_number}")
            if agencies is not None:
                all_data.setdefault("AdministrativeCodeGetAgencyListOfJson", {})[title_number] = agencies

                for agency in agencies.get("AgencyList", []):
                    agency_number = agency["AgencyNumber"]
                    preface = fetch_data(BASE_URL + f"AdministrativeCodePrefaceJson/{title_number}/{agency_number}")
                    if preface is not None:
                        all_data.setdefault("AdministrativeCodePrefaceJson", {})[f"{title_number}_{agency_number}"] = preface

                    chapters = fetch_data(BASE_URL + f"AdministrativeCodeChapterListOfJson/{title_number}/{agency_number}")
                    if chapters is not None:
                        all_data.setdefault("AdministrativeCodeChapterListOfJson", {})[f"{title_number}_{agency_number}"] = chapters

                        for chapter in chapters.get("ChapterList", []):
                            chapter_number = chapter.get("ChapterNumber")
                            if chapter_number:
                                sections = fetch_data(BASE_URL + f"AdministrativeCodeGetSectionListOfJson/{title_number}/{agency_number}/{chapter_number}")
                                if sections is not None:
                                    all_data.setdefault("AdministrativeCodeGetSectionListOfJson", {})[f"{title_number}_{agency_number}_{chapter_number}"] = sections

                                    for section in sections.get("SectionList", []):
                                        section_number = section.get("SectionNumber")
                                        if section_number:
                                            section_details = fetch_data(BASE_URL + f"AdministrativeCodeGetSectionDetailsJson/{title_number}/{agency_number}/{chapter_number}/{section_number}/0/0")
                                            if section_details is not None:
                                                all_data.setdefault("AdministrativeCodeGetSectionDetailsJson", {})[f"{title_number}_{agency_number}_{chapter_number}_{section_number}"] = section_details

    # Authorities Data
    authorities = fetch_data(BASE_URL + "AuthoritiesGetListOfJson")
    if authorities is not None:
        all_data["AuthoritiesGetListOfJson"] = authorities

        for authority in authorities:
            short_name = authority.get("ShortName")
            if short_name:
                authority_detail = fetch_data(BASE_URL + f"AuthoritiesGetDetailJson/{short_name}")
                if authority_detail is not None:
                    all_data.setdefault("AuthoritiesGetDetailJson", {})[short_name] = authority_detail

    # Charters Data
    charters = fetch_data(BASE_URL + "ChartersGetListOfJson")
    if charters is not None:
        all_data["ChartersGetListOfJson"] = charters

        for charter in charters:
            short_name = charter.get("ShortName")
            if short_name:
                charter_detail = fetch_data(BASE_URL + f"ChartersGetDetailJson/{short_name}")
                if charter_detail is not None:
                    all_data.setdefault("ChartersGetDetailJson", {})[short_name] = charter_detail

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

    # Compacts Data
    compacts = fetch_data(BASE_URL + "CompactsTitlesGetListOfJson")
    if compacts is not None:
        all_data["CompactsGetListOfJson"] = compacts

        for compact in compacts:
            short_name = compact.get("ShortName")
            if short_name:
                compact_detail = fetch_data(BASE_URL + f"CompactSectionsGetSectionDetailsJson/{short_name}")
                if compact_detail is not None:
                    all_data.setdefault("CompactSectionsGetSectionDetailsJson", {})[short_name] = compact_detail

    # Constitution Data
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

    # Uncodified Acts Data
    
    current_year = datetime.now().year 
    years = list(range(1946, current_year + 1))
    for year in years:
        chapters = fetch_data(BASE_URL + f"UncodifiedActChapterByYearGetListOfJson/{year}")
        if chapters is not None:
            all_data.setdefault("UncodifiedActChapterByYearGetListOfJson", {})[year] = chapters

    return all_data

def save_data_as_per_schema(data):
    with open('comprehensive_VA_code.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("All data has been successfully fetched and saved in 'comprehensive_VA_code.json'")

if __name__ == "__main__":
    all_data = gather_all_data()
    save_data_as_per_schema(all_data)
