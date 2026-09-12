import base64
import io
import pandas as pd
import pypdf
from PIL import Image
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Talous-AI & Vaurastumisassistentti", page_icon="📈", layout="centered"
)

st.title("📈 Talous-AI & Vaurastumisassistentti (Pro)")
st.write(
    "Kattava talousvalmentaja, sijoituspuskurin laskija, älykäs budjetoija, "
    "palkkalaskelmien PDF-lukija sekä tarkalla tekoälyllä varustettu työkalu."
)

# Sivupalkki asetuksille
st.sidebar.header("⚙️ Asetukset & Versio")
app_mode = st.sidebar.selectbox(
    "Valitse tila", ["Ilmaisversio (Free)", "Pro-versio (Testaa)"]
)
api_key = st.sidebar.text_input("Syötä OpenAI API-avain", type="password")

# Pääsovelluksen välilehdet (kaikki vanhat ja uudet mukana)
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📝 Tulot, PDF & Menot", 
        "🎯 Sijoituspuskuri & -opas", 
        "💡 Smart Budget", 
        "🛒 Ruokalista, Budjetti & Kauppavinkit",
        "🏷️ Omat Hinnat & Kuittiskanneri"
    ]
)

# Alustetaan muuttujat session stateen
if "custom_products" not in st.session_state:
    st.session_state.custom_products = pd.DataFrame(
        [
            {"Poista": False, "Tuote / Pakkaus": "Kanafilee (400g)", "Kauppa": "Prisma", "Hinta (€)": 4.50},
            {"Poista": False, "Tuote / Pakkaus": "Maito (1l)", "Kauppa": "S-Market", "Hinta (€)": 1.19},
            {"Poista": False, "Tuote / Pakkaus": "Raejuusto (400g)", "Kauppa": "Prisma", "Hinta (€)": 2.15},
            {"Poista": False, "Tuote / Pakkaus": "Banaanit (niput)", "Kauppa": "Lidl", "Hinta (€)": 2.50},
            {"Poista": False, "Tuote / Pakkaus": "Riisi (1kg)", "Kauppa": "K-Citymarket", "Hinta (€)": 1.60},
        ]
    )

if "uploaded_image_records" not in st.session_state:
    st.session_state.uploaded_image_records = []

if "extracted_pdf_income" not in st.session_state:
    st.session_state.extracted_pdf_income = 0.0


def compress_image(image_bytes, max_size=1600):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((max_size, max_size))
        buffered = io.BytesIO()
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(buffered, format="JPEG", quality=90)
        return buffered.getvalue()
    except Exception:
        return image_bytes


def encode_image(image_bytes):
    compressed_bytes = compress_image(image_bytes)
    return base64.b64encode(compressed_bytes).decode("utf-8")


with tab1:
    st.subheader("1. Tulot (myös PDF-palkkalaskelman luku) & Manuaaliset menot")
    
    st.markdown("### 📄 Tuo tulotiedot suoraan PDF-palkkalaskelmasta")
    uploaded_pdf = st.file_uploader("Lataa palkkalaskelma (PDF)", type=["pdf"])
    
    if uploaded_pdf is not None:
        try:
            reader = pypdf.PdfReader(uploaded_pdf)
            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text() or ""
            
            if api_key and pdf_text.strip():
                with st.spinner("Tekoäly lukee palkkatietoja PDF:stä..."):
                    client = OpenAI(api_key=api_key)
                    prompt = (
                        "Etsi seuraavasta palkkalaskelman tekstistä NETTO-palkka (käteen jäävä summa) "
                        "sekä BRUTTO-palkka. Palauta tulos puhtaana numerona muodossa: "
                        "Netto: [numero], Brutto: [numero]. Jos et löydä varmaa summaa, arvioi tai laita 0.\n\n"
                        f"Teksti:\n{pdf_text[:3000]}"
                    )
                    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
                    ai_answer = resp.choices[0].message.content
                    st.info(f"AI:n löytämät tiedot tekstistä: {ai_answer}")
            else:
                st.write("PDF luettu (syötä API-avain sivupalkkiin, jos haluat tekoälyn jäsentävän summan automaattisesti).")
        except Exception as e:
            st.error(f"Virhe PDF-tiedoston lukemisessa: {e}")

    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input("Netto-kuukausitulot (€)", min_value=0.0, value=2500.0, step=50.0)
        vuokra = st.number_input("Vuokra / Asuntolaina (€)", min_value=0.0, value=800.0, step=50.0)
        sahko = st.number_input("Sähkö (€)", min_value=0.0, value=40.0, step=10.0)
        vesi = st.number_input("Vesi (€)", min_value=0.0, value=20.0, step=5.0)
    with col2:
        ruokakulut = st.number_input("Arvioidut ruokakulut (kauppa) (€)", min_value=0.0, value=350.0, step=25.0)
        suoratoisto = st.number_input("Suoratoistopalvelut (€)", min_value=0.0, value=45.0, step=5.0)
        muut_menot = st.number_input("Muut pakolliset kulut (€)", min_value=0.0, value=150.0, step=25.0)

    total_expenses = vuokra + sahko + vesi + ruokakulut + suoratoisto + muut_menot
    net_left = monthly_income - total_expenses
    st.info(f"📊 Yhteenveto: Tulot {monthly_income} € | Menot **{total_expenses} €** | Jäljelle jää: **{net_left} €**")


with tab2:
    st.subheader("2. Sijoittamiskeskeinen optimointi, Markkinatuoton laskenta & Kriittinen AI-analyysi")
    current_balance = st.number_input("Tilillä oleva nykyinen käyttöraha yhteensä (€)", value=3500.0)
    buffer_need = st.number_input("Turvapuskurin tavoite (€)", value=2000.0)

    if st.button("Laske sijoitettava ylijäämä"):
        excess_cash = current_balance - buffer_need
        if excess_cash > 0:
            st.success(
                f"💡 **Sijoituspotentiaali:** Tililläsi on noin **{excess_cash:.0f} euroa** "
                "ylimääräistä puskurin ylittävää rahaa."
            )
        else:
            st.info("Keskity ensin saavuttamaan turvapuskuritavoite.")

    st.markdown("---")
    st.markdown("### 📈 Markkinatuotto- ja Korkoa korolle -laskuri")
    
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        alkup_sijoitus = st.number_input("Alkusijoitus (€)", value=1000.0, step=100.0)
        kk_sijoitus = st.number_input("Kuukausisäästö / -sijoitus (€)", value=150.0, step=25.0)
    with col_inv2:
        sijoitus_aika_vuotta = st.slider("Sijoitusaika (vuotta)", 1, 40, 10)
        arvioitu_tuotto_prosentti = st.slider("Arvioitu vuosituotto (%)", 0.0, 20.0, 7.0, 0.5)

    kokonaissumma = alkup_sijoitus
    kuukausi_tuotto = arvioitu_tuotto_prosentti / 100 / 12
    kuukausia = sijoitus_aika_vuotta * 12

    sijoitettu_paoma_yhteensa = alkup_sijoitus
    for _ in range(kuukausia):
        kokonaissumma = (kokonaissumma + kk_sijoitus) * (1 + kuukausi_tuotto)
        sijoitettu_paoma_yhteensa += kk_sijoitus

    tuotto_yhteensa = kokonaissumma - sijoitettu_paoma_yhteensa

    st.info(
        f"📊 **Laskelman tulos ({sijoitus_aika_vuotta} vuoden jälkeen):**\n\n"
        f"- Sijoitettu pääoma yhteensä: **{sijoitettu_paoma_yhteensa:,.0f} €**\n"
        f"- Arvioitu voitto / tuotto: **{tuotto_yhteensa:,.0f} €**\n"
        f"- **Salkun arvo yhteensä:** **{kokonaissumma:,.0f} €**"
    )

    st.markdown("### 🤖 Kriittinen tekoälyanalyysi sijoitussuunnitelmasta")
    sijoitus_kohde_kuvaus = st.text_area(
        "Kerro lyhyesti mihin aiot sijoittaa (esim. globaalit indeksirahastot, kryptot, yksittäiset osakkeet tai asunnot):",
        "Sijoitan kuukausittain maailma-indeksirahastoon (kuten EUNL) ja toivon n. 7% keskimääräistä tuottoa."
    )

    if st.button("Pyydä kriittinen AI-analyysi sijoituksistasi"):
        if not api_key:
            st.warning("Syötä sivupalkkiin OpenAI API-avain.")
        else:
            client = OpenAI(api_key=api_key)
            prompt = (
                f"Olet äärimmäisen kriittinen, realistinen ja kokenut sijoitusasiantuntija. "
                f"Analysoi seuraavaa sijoitussuunnitelmaa:\n"
                f"- Alkusijoitus: {alkup_sijoitus} €\n"
                f"- Kuukausisijoitus: {kk_sijoitus} €\n"
                f"- Sijoitusaika: {sijoitus_aika_vuotta} vuotta\n"
                f"- Oletettu vuosituotto: {arvioitu_tuotto_prosentti} %\n"
                f"- Sijoituskohteet ja strategia: {sijoitus_kohde_kuvaus}\n\n"
                "Ole rehellinen riskeistä (inflaatio, markkinoiden laskukaudet eli karhumarkkinat, verotus, epärealistiset odotukset, hajautus). "
                "Älä kaunista totuutta, vaan anna rakentavaa, mutta tiukkaa ja realistista palautetta."
            )
            with st.spinner("Tekoäly analysoi sijoituksiasi kriittisesti..."):
                resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
                st.markdown(resp.choices[0].message.content)

    st.markdown("---")
    st.markdown("### 📊 Laajennettu sijoitusopas & vaihtoehdot")
    st.info("⚠️ **Vastuuvapauslauseke:** Tämä työkalu on tarkoitettu vain oppimiseen ja budjetointiin, eikä se ole virallinen sijoitusneuvo tai kehotus ostaa tiettyjä arvopapereita. Sijoittamiseen liittyy aina riski pääoman menettämisestä.")
    
    sijoitus_vaihtoehto = st.selectbox(
        "Valitse omaisuuslaji, josta haluat lisätietoja:",
        [
            "Osakkeet & Indeksirahastot / ETF:ät", 
            "Korkosijoitukset (Säästötilit / Valtiolainat)", 
            "Kiinteistöt & Asuntosijoittaminen", 
            "Kryptovaluutat & Korkean riskin kohteet",
            "Vertaislainat (Peer-to-Peer)"
        ]
    )
    
    if sijoitus_vaihtoehto == "Osakkeet & Indeksirahastot / ETF:ät":
        st.write("""
        * **Indeksirahastot & ETF:ät:** Hajautettu sijoituspaketti, joka seuraa laajoja markkinoita (esim. S&P 500 tai MSCI World). Sopii pitkäjänteiselle sijoittajalle matalien kulujen ja helpon hajautuksen ansiosta.
        * **Suorat osakkeet:** Yksittäisen yrityksen omistusosuus. Vaatii syvempää perehtymistä ja kantaa suurempaa hajautusriskiä, mutta voi tarjota paremman tuoton onnistuessaan.
        """)
    elif sijoitus_vaihtoehto == "Korkosijoitukset (Säästötilit / Valtiolainat)":
        st.write("""
        * **Korkosijoitukset:** Matalamman riskin vaihtoehto, kuten määräaikaistilit, säästötilit tai valtion joukkovelkakirjalainat. Tuotto-odotus on maltillisempi, mutta suojaa pääomaa epävarmoina aikoina.
        """)
    elif sijoitus_vaihtoehto == "Kiinteistöt & Asuntosijoittaminen":
        st.write("""
        * **Asuntosijoittaminen:** Vuokratuottoa ja mahdollista arvonnousua. Vaatii usein isomman alkupääoman tai velkavipua (asuntolainaa), ja siihen liittyy vuokralaisriskejä sekä yhtiövastikkeiden nousupaineita.
        * **Kiinteistörahastot (REITit):** Pienemmällä summalla hajautetusti kiinteistöihin pörssin kautta.
        """)
    elif sijoitus_vaihtoehto == "Kryptovaluutat & Korkean riskin kohteet":
        st.write("""
        * **Kryptovaluutat (esim. Bitcoin, Ethereum):** Erittäin korkean volatiliteetin ja riskin sijoituskohteet. Arvo voi nousta tai laskea rajusti lyhyessä ajassa. Suositellaan vain pieneksi mausteeksi salkkuun (esim. 1–5%).
        """)
    else:
        st.write("""
        * **Vertaislainat:** Lainaat rahaa kuluttajille tai yrityksille alustojen kautta. Korkeat korot kompensoivat luottotappioriskiä; vaatii tarkkaa hajauttamista useisiin lainoihin.
        """)


with tab3:
    st.subheader("3. Smart Budget & Viikkoseuranta")
    weekly_food_target = st.number_input("Asetettu viikoittainen ruokabudjetti (€)", value=80.0)
    actual_food_spent = st.number_input("Tällä viikolla ruokaan käytetty (€)", value=65.0)
    
    if st.button("Hae palaute viikon kulutuksesta"):
        if not api_key:
            st.warning("Syötä sivupalkkiin OpenAI API-avain.")
        else:
            client = OpenAI(api_key=api_key)
            prompt = f"Arvioi viikoittaista ruokabudjettia (tavoite: {weekly_food_target} €, toteutunut: {actual_food_spent} €) huumorilla ja anna vinkkejä."
            resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
            st.markdown(resp.choices[0].message.content)


with tab4:
    st.subheader("4. Perusruokabudjetoija, Ruokalista & Kauppavinkit")
    talouden_koko = st.selectbox(
        "Valitse talouden koko (henkilömäärä)", 
        ["1 henkilö", "2 henkilöä", "Perhe (3-4 hlö)", "Suuri perhe (5+ hlö)"]
    )
    
    kerroin = {"1 henkilö": 1.0, "2 henkilöä": 1.8, "Perhe (3-4 hlö)": 2.8, "Suuri perhe (5+ hlö)": 3.8}[talouden_koko]
    arvioitu_viikkobudjetti = int(70 * kerroin)
    
    st.success(f"🛒 Valitulla talouden koolla (**{talouden_koko}**) suositusviikkobudjetti ruokaostoksille on noin **{arvioitu_viikkobudjetti} € / viikko**.")
    
    st.markdown("#### Viikon helppo ja edullinen ruokalista")
    st.write("""
    * **Maanantai:** Juuressoppa ja ruisleipä
    * **Tiistai:** Makaronilaatikko (kasvis- tai jauheliha)
    * **Keskiviikko:** Kirjolohikeitto
    * **Torstai:** Texmex-pavut tai kanakastike ja riisi
    * **Perjantai:** Itsetehdyt uunipizzat edullisista raaka-aineista
    """)
    
    st.markdown("#### Älykkäät kauppavinkit")
    st.write("""
    * Hyödynnä sesongin kasviksia.
    * Suunnittele viikon ruokalista etukäteen, jotta heräteostokset vähenevät.
    * Tarkkaile kilohintoja tuotevertailussa.
    """)


with tab5:
    st.subheader("🏷️ Omat tuotehinnat, Kaupat & Älykäs Kuvaskanneri")
    st.write("Lataa kauppojen näyttökuvat tai kuitit. Aiemmin lisätyt tai järjestelmään kertaalleen tallennetut kuvat merkitään selkeän **punaiseksi**.")

    col_c1, col_c2 = st.columns([1, 1])

    with col_c1:
        st.markdown("### 📸 Monikuva- / Näyttökuvaskanneri")
        
        default_store_choice = st.selectbox(
            "Valitse oletuskauppa (jos kuvasta ei selviä):",
            ["Päättele kuvasta", "Prisma", "S-Market", "Lidl", "K-Citymarket", "K-Market", "Alepa", "Sale"]
        )

        uploaded_files = st.file_uploader(
            "Lataa kauppojen näyttökuvat tai kuitit", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.read()
                
                exists_already = any(
                    item["name"] == uploaded_file.name and item["data"] == file_bytes 
                    for item in st.session_state.uploaded_image_records
                )
                
                if not exists_already:
                    st.session_state.uploaded_image_records.append({
                        "name": uploaded_file.name,
                        "data": file_bytes,
                        "type": "image/jpeg",
                        "already_added": False
                    })

        if st.session_state.uploaded_image_records:
            st.markdown("#### Ladatut kuvat & hallinta (Rastita poistaaksesi)")
            
            updated_records = []
            for i, record in enumerate(st.session_state.uploaded_image_records):
                name_count = sum(1 for r in st.session_state.uploaded_image_records if r["name"] == record["name"])
                is_red = name_count > 1 or record.get("already_added", False)

                if is_red:
                    st.markdown(
                        f"""<div style="border: 3px solid #ff4d4d; background-color: #ffe6e6; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                        <span style="color: #cc0000; font-weight: bold; font-size: 15px;">🛑 Jo lisätty / Käsitelty aiemmin: {record['name']}</span>
                        </div>""", 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""<div style="border: 2px solid #4CAF50; background-color: #e8f5e9; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                        <span style="color: #2e7d32; font-weight: bold;">✨ Uusi kuva: {record['name']}</span>
                        </div>""", 
                        unsafe_allow_html=True
                    )
                
                cols = st.columns([3, 1])
                with cols[0]:
                    st.image(record["data"], caption=record["name"], width=160)
                with cols[1]:
                    remove_flag = st.checkbox("Poista", key=f"del_img_{i}")
                
                if not remove_flag:
                    updated_records.append(record)
                else:
                    st.warning(f"Poistettu kuva: {record['name']}")
            
            st.session_state.uploaded_image_records = updated_records

        if st.session_state.uploaded_image_records and st.button("Pura tuotteet, kaupat ja tarkat hinnat kuvista (Tarkka analyysi)"):
            if not api_key:
                st.warning("Syötä sivupalkkiin OpenAI API-avain.")
            else:
                with st.spinner("Tekoäly (gpt-4o) tutkii kuvia perusteellisesti..."):
                    client = OpenAI(api_key=api_key)
                    store_inst = f"Käytä oletuskauppana '{default_store_choice}' jos kauppaa ei selvästi mainita. " if default_store_choice != "Päättele kuvasta" else "Tunnista aina kaupan nimi suoraan kuvasta. "
                    
                    messages_content = [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        f"Olet äärimmäisen tarkka kauppa-, tuote- ja hintatietojen asiantuntija. {store_inst} "
                                        "Skannaa kaikki tuoterivit, tuotenimet, pakkauskoot sekä hinnat euroina (€). "
                                        "Palauta tulos selkeänä taulukkona tai listana muodossa:\n"
                                        "Tuote / Pakkaus | Kauppa | Hinta (€)"
                                    )
                                }
                            ]
                        }
                    ]

                    for record in st.session_state.uploaded_image_records:
                        base64_img = encode_image(record["data"])
                        messages_content[0]["content"].append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_img}"
                            }
                        })
                        record["already_added"] = True

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages_content,
                        max_tokens=2000,
                        temperature=0.1
                    )

                    st.success("Tarkka kuvien analyysi valmis!")
                    st.markdown("### 🔍 Löydetyt tuotteet, kaupat ja hinnat:")
                    st.markdown(response.choices[0].message.content)

    with col_c2:
        st.markdown("### 📋 Omat tallennetut hinnat & kaupat")
        edited_df = st.data_editor(st.session_state.custom_products, num_rows="dynamic", key="product_editor")
        
        if "Poista" in edited_df.columns:
            st.session_state.custom_products = edited_df[edited_df["Poista"] == False].reset_index(drop=True)
        else:
            st.session_state.custom_products = edited_df
