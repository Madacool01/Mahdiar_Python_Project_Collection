import flet as ft
import pandas as pd
import os
import sys
import json

from scraper import scrape_jobs_for_all_keywords


#Adzuna search keywords -------- JSON Keyword Save logic
KEYWORD_FILE = "keywords.json"
KEYWORDS = ["maschienenbau", "projectleiter", "projectengineur",
        "produktmanager", "mechanischer berechner", "mechanical design engineer", "mechanischer konstrukteur", "CAD-Konstrukteur", "Mechanical Engineer"]

def load_keywords():
    #Loads keywords from JSON. If doesnt exist it create a default one
    if os.path.exists(KEYWORD_FILE):
        with open(KEYWORD_FILE, "r") as f:
            return json.load(f)
    else:
        with open(KEYWORD_FILE, "w") as f:
            json.dump(KEYWORDS, f)
        return KEYWORDS
    
def save_keywords(keyword_list):
    with open(KEYWORD_FILE, "w") as f:
        json.dump(keyword_list, f)

async def main(page: ft.Page):

    page.title = "Job Scraper Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.dark_theme = ft.Theme(color_scheme_seed="#0073BB")
    page.update()
    page.window.width = 800
    page.window.height = 900
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO

    title = ft.Text("Job Scraper Pro", size=40, weight=ft.FontWeight.BOLD)


    #Radius km slider
    radius_text = ft.Text(f"Search Radius: 400 km", size=16)

    def on_radius_change(e):
        radius_text.value = f"Search Radius: {int(radius_slider.value)} km"

    radius_slider = ft.Slider(
        min=0, max=400, divisions=40, value=400,
        label="{value} km", width=400, on_change=on_radius_change 
    )

    whole_country_switch = ft.Switch(label="Search Entire Austria", value=False)

    def on_switch_change(e):
        if whole_country_switch.value == True:
            location_input.disabled = True
            radius_slider.disabled = True
        else:
            location_input.disabled = False
            radius_slider.disabled = False
        page.update()
    
    whole_country_switch.on_change = on_switch_change

    location_input = ft.TextField(label="Location (German Name):", hint_text="e.g Linz, Wien ", width=400)

    saved_keywords = load_keywords()
    checkboxes = []

    checkbox_row = ft.Row(wrap=True, width=700)

    def render_checkboxes():
        checkbox_row.controls.clear()
        checkboxes.clear()
        for kw in saved_keywords:
            cb = ft.Checkbox(label=kw.capitalize(), value=True)
            checkboxes.append(cb)
            checkbox_row.controls.append(cb)
        page.update()

    render_checkboxes()

    def toggle_all_checkboxes(e):
        target_state = not checkboxes[0].value if checkboxes else True
        for cb in checkboxes:
            cb.value = target_state
        page.update()

    selected_deselect_all_btn = ft.TextButton("Select / Deselect All", on_click=toggle_all_checkboxes)
    
    new_keyword_input = ft.TextField(label="Add new keyword...", width=250, height=40) #Add new keyword

    def add_keyword(e):
        new_word = new_keyword_input.value.strip()
        if not new_word:
            page.show_dialog(ft.SnackBar(ft.Text("Please Enter a Valid Keyword.")))
        if new_word and new_word not in saved_keywords:
            saved_keywords.append(new_word)
            save_keywords(saved_keywords) #save json file
            render_checkboxes()
            new_keyword_input.value = "" #clear input box
            page.update()

    add_keyword_btn = ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=ft.Colors.GREEN_400, on_click=add_keyword)

    progress_ring = ft.ProgressRing(visible=False)
    status_text = ft.Text("", color=ft.Colors.YELLOW_400, italic=True)

    def run_search(e):
        active_keywords = [cb.label for cb in checkboxes if cb.value == True]

        if whole_country_switch.value == False and not location_input.value: #City search with empty location
            # status_text.value = "⚠️ Please enter a valid search location!"
            page.show_dialog(ft.SnackBar(content="⚠️ Please enter a valid search location!", bgcolor="#FFDD00"))
            location_input.error = "⚠️ Please enter a valid search location!"
            status_text.color = ft.Colors.RED_400
            page.update()
            return

        search_btn.disabled = True
        progress_ring.visible = True
        status_text.color = ft.Colors.YELLOW_400

        try:
            #Scrape jobs
            location_argument = None if whole_country_switch.value else location_input.value 

            if location_argument:
                status_text.value = f"🌐 Scraping jobs in {location_input.value}..."
            else:
                status_text.value = f"🌐 Scraping jobs in WHOLE AUSTRIA..."
            page.update()
            jobs_dict = scrape_jobs_for_all_keywords(
                active_keywords, 
                location=location_argument, #Actual location or None!! 
                radius_km=int(radius_slider.value))

            true_count = 0
            for cb in checkboxes:
                if cb.value is True:
                    true_count+=1

            if true_count == 0:
                page.show_dialog(ft.SnackBar(content="⚠️ Please select at least 1 keyword!", bgcolor="#FFC800"))
                search_btn.disabled = False
                progress_ring.visible = False
                page.update()

            else:
                if len(jobs_dict) == 0:
                    status_text.value = "⚠️ No jobs found in this area..."
                    page.show_dialog(ft.SnackBar(content="⚠️ No jobs found in this area...", bgcolor="#FFC800"))
                    search_btn.disabled = False
                    progress_ring.visible = False
                    page.update()
                    return 
            
            #Export to excel
            status_text.value = "💾 Generating Excel Report..."
            page.update()

            df = pd.DataFrame.from_dict(jobs_dict, orient="index")
            df = df.sort_values(by="Company", ascending=True)
            df = df.drop(columns="Description", errors="ignore")

            if getattr(sys, 'frozen', False):
                save_dir = os.path.dirname(os.path.abspath(sys.executable))
            else:
                save_dir = os.path.dirname(os.path.abspath(__file__))
            excel_filename = os.path.join(save_dir, "Jobs_Found.xlsx")

            writer = pd.ExcelWriter(excel_filename, engine="xlsxwriter")
            df.to_excel(writer, sheet_name='Top Job Matches', index=False)

            worksheet = writer.sheets['Top Job Matches']
            worksheet.set_column('A:A', 35) #Job Title wider
            worksheet.set_column('B:B', 25) # Company wider
            worksheet.set_column('C:C', 50)
            worksheet.set_column('D:D', 20)
            writer.close()

            status_text.value = f"🎉 Success! Saved to Jobs_Found.xlsx"
            page.show_dialog(ft.SnackBar(ft.Container(
                content=ft.Text(
                    "Success! Saved to Jobs_Found.xlsx",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
            ),
            bgcolor="#71FF9E"))
            status_text.color = ft.Colors.GREEN_400

        except Exception as err:
            status_text.value = f"❌ Error: {str(err)}"
            status_text.color = ft.Colors.RED_400

        finally:
            search_btn.disabled = False
            progress_ring.visible = False
            page.update()

    search_btn = ft.FilledButton("Scrape & Analyze Jobs", icon=ft.Icons.SEARCH, on_click=run_search)

    #Stack everything into a vertical column
    main_layout = ft.Column(
        controls=[
            title, 
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT), #Invisible spacing

            #Location & Radius
            ft.Text("Search Area", style=ft.TextStyle(weight=ft.FontWeight.BOLD)),
            whole_country_switch,
            location_input,
            radius_text,
            radius_slider,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

            # Keywords and Checkboxes
            ft.Text("Target Keywords: ", weight=ft.FontWeight.BOLD),
            ft.Row([new_keyword_input, add_keyword_btn, selected_deselect_all_btn]),
            checkbox_row,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

            search_btn,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Row([progress_ring, status_text])
            
        ],
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    page.add(main_layout)


if __name__ == "__main__":
    ft.run(main)