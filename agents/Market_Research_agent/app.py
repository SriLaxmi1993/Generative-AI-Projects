import os
import asyncio
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.models.openai import OpenAIChat
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="AI DeepResearch Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for API keys
st.sidebar.header("⚙️ Configuration")

# API key inputs
openai_api_key = st.sidebar.text_input(
    "OpenAI API Key", 
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
    help="Get your API key from https://platform.openai.com"
)

serpapi_key = st.sidebar.text_input(
    "SerpApi Key", 
    value=os.getenv("SERPAPI_KEY", ""),
    type="password",
    help="Get your API key from https://serpapi.com"
)

perplexity_api_key = st.sidebar.text_input(
    "Perplexity API Key (Optional)", 
    value=os.getenv("PERPLEXITY_API_KEY", ""),
    type="password",
    help="Get your API key from https://www.perplexity.ai/settings/api"
)

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This AI DeepResearch Agent uses OpenAI's models and SerpApi/Perplexity search to perform comprehensive research on any topic. "
    "It generates research questions, finds answers, and compiles a professional report."
)

st.sidebar.markdown("### Tools Used")
st.sidebar.markdown("- 🔍 SerpApi (Google Search API)")
st.sidebar.markdown("- 🧠 Perplexity AI (Optional)")
st.sidebar.markdown("- 📄 Export Options (PDF, Markdown, JSON)")

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'question_answers' not in st.session_state:
    st.session_state.question_answers = []
if 'question_sources' not in st.session_state:
    st.session_state.question_sources = []
if 'report_content' not in st.session_state:
    st.session_state.report_content = ""
if 'research_complete' not in st.session_state:
    st.session_state.research_complete = False
if 'research_history' not in st.session_state:
    st.session_state.research_history = []
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = ""
if 'current_domain' not in st.session_state:
    st.session_state.current_domain = ""

# Main content
st.title("🔍 AI DeepResearch Agent with Agno")

# Function to initialize the LLM
def initialize_agents(openai_key, serpapi_key, perplexity_key):
    # Initialize OpenAI LLM
    llm = OpenAIChat(id="gpt-4", api_key=openai_key)
    
    return llm, serpapi_key, perplexity_key

# Function to search using SerpApi
def search_serpapi(serpapi_key, query):
    """Search using SerpApi and return results with sources"""
    if not serpapi_key:
        return "", []
    
    try:
        url = "https://serpapi.com/search"
        params = {
            'api_key': serpapi_key,
            'engine': 'google',
            'q': query,
            'num': 5
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        
        sources = []
        content_parts = []
        
        # SerpApi returns results in 'organic_results' key
        if 'organic_results' in results:
            for item in results['organic_results'][:5]:
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                link = item.get('link', '')
                sources.append({
                    'title': title,
                    'url': link,
                    'snippet': snippet
                })
                content_parts.append(f"{title}: {snippet}")
        
        content = "\n\n".join(content_parts)
        return content, sources
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            # API key issue
            st.warning(f"SerpApi authentication failed. Please check your API key. Error: {str(e)}")
        elif e.response.status_code == 429:
            st.warning(f"SerpApi rate limit exceeded. Please try again later. Error: {str(e)}")
        else:
            st.warning(f"SerpApi error: {str(e)}")
        return "", []
    except Exception as e:
        st.warning(f"Error searching with SerpApi: {str(e)}")
        return "", []

# Function to search using Perplexity AI
def search_perplexity(perplexity_api_key, query):
    """Search using Perplexity API and return results"""
    if not perplexity_api_key:
        return ""
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            'Authorization': f'Bearer {perplexity_api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'llama-3.1-sonar-large-128k-online',
            'messages': [
                {
                    'role': 'system',
                    'content': 'Be precise and concise.'
                },
                {
                    'role': 'user',
                    'content': query
                }
            ],
            'max_tokens': 500,
            'temperature': 0.2
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json()
        
        if 'choices' in results and len(results['choices']) > 0:
            return results['choices'][0]['message']['content']
        return ""
    except Exception as e:
        # Silently fail if Perplexity is not available
        return ""

# Function to create agents
def create_question_generator(llm, question_count, question_type):
    """Create question generator agent based on question type"""
    question_type_instructions = {
        "yes/no": "Generate exactly {count} specific yes/no research questions.",
        "open-ended": "Generate exactly {count} open-ended research questions that require detailed explanations.",
        "comparative": "Generate exactly {count} comparative research questions that compare different aspects or entities.",
        "analytical": "Generate exactly {count} analytical research questions that require deep analysis and evaluation."
    }
    
    instruction_template = question_type_instructions.get(question_type, question_type_instructions["yes/no"])
    
    question_generator = Agent(
        name="Question Generator",
        model=llm,
        instructions=f"""
        You are an expert at breaking down research topics into specific questions.
        {instruction_template.format(count=question_count)}
        Respond ONLY with the text of the {question_count} questions formatted as a numbered list, and NOTHING ELSE.
        """
    )
    
    return question_generator

# Function to extract questions after think tag
def extract_questions_after_think(text):
    if "</think>" in text:
        return text.split("</think>", 1)[1].strip()
    return text.strip()

# Function to generate research questions
def generate_questions(llm, topic, domain, question_count, question_type):
    question_generator = create_question_generator(llm, question_count, question_type)
    
    with st.spinner("🤖 Generating research questions..."):
        questions_task: RunOutput = question_generator.run(
            input=f"Generate exactly {question_count} {question_type} research questions about the topic '{topic}' in the domain '{domain}'."
        )
        questions_text = questions_task.content
        questions_only = extract_questions_after_think(questions_text)
        
        # Extract questions into a list
        questions_list = [q.strip() for q in questions_only.split('\n') if q.strip() and (q.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')) or not q.strip()[0].isdigit())]
        # Clean up question numbers
        cleaned_questions = []
        for q in questions_list:
            # Remove leading numbers and dots
            cleaned = q.lstrip('0123456789. ').strip()
            if cleaned:
                cleaned_questions.append(cleaned)
        
        st.session_state.questions = cleaned_questions[:question_count]
        return st.session_state.questions

# Async function to research a specific question
async def research_question_async(llm, serpapi_key, perplexity_api_key, topic, domain, question):
    """Research a question asynchronously"""
    # Search with SerpApi first
    serpapi_content, serpapi_sources = search_serpapi(serpapi_key, f"{topic} {domain} {question}")
    
    # Search with Perplexity if available
    perplexity_content = search_perplexity(perplexity_api_key, f"{topic} {domain} {question}")
    
    # Combine search results
    combined_context = f"Google Search Results (via SerpApi):\n{serpapi_content}\n\n"
    if perplexity_content:
        combined_context += f"Perplexity AI Analysis:\n{perplexity_content}\n\n"
    
    # Create research agent
    research_task = Agent(
        model=llm,
        instructions=f"""You are a sophisticated research assistant. Answer the following research question about the topic '{topic}' in the domain '{domain}':\n\n{question}\n\n
        Use the search results provided below to provide a concise, well-sourced answer.
        Include citations with URLs when referencing sources.
        Format your answer clearly with proper structure.
        
        {combined_context}
        """
    )
    
    research_result: RunOutput = research_task.run(input=question)
    return research_result.content, serpapi_sources

# Function to research questions in parallel
async def research_questions_parallel(llm, serpapi_key, perplexity_api_key, topic, domain, questions):
    """Research multiple questions in parallel"""
    tasks = [
        research_question_async(llm, serpapi_key, perplexity_api_key, topic, domain, q)
        for q in questions
    ]
    results = await asyncio.gather(*tasks)
    return results

# Function to compile final report
def compile_report(llm, topic, domain, question_answers, question_sources):
    with st.spinner("📝 Compiling final report..."):
        qa_sections = "\n".join(
            f"<h2>{idx+1}. {qa['question']}</h2>\n<p>{qa['answer']}</p>" 
            for idx, qa in enumerate(question_answers)
        )
        
        # Compile citations
        all_sources = []
        for sources in question_sources:
            all_sources.extend(sources)
        
        # Remove duplicates
        unique_sources = []
        seen_urls = set()
        for source in all_sources:
            if source['url'] not in seen_urls:
                unique_sources.append(source)
                seen_urls.add(source['url'])
        
        citations_html = "\n".join(
            f"<li><a href='{s['url']}'>{s['title']}</a></li>"
            for s in unique_sources[:20]  # Limit to top 20 sources
        )
        
        compile_report_task = Agent(
            name="Report Compiler",
            model=llm,
            instructions=f"""
            You are a sophisticated research assistant. Compile the following research findings into a professional, McKinsey-style report. The report should be structured as follows:

            1. Executive Summary/Introduction: Briefly introduce the topic and domain, and summarize the key findings.
            2. Research Analysis: For each research question, create a section with a clear heading and provide a detailed, analytical answer. Do NOT use a Q&A format; instead, weave the answer into a narrative and analytical style.
            3. Conclusion/Implications: Summarize the overall insights and implications of the research.
            4. Sources and Citations: Include a references section.

            Use clear, structured HTML for the report.

            Topic: {topic}
            Domain: {domain}

            Research Questions and Findings (for your reference):
            {qa_sections}

            Sources:
            {citations_html}

            Generate a comprehensive, well-structured HTML report. Do not mention Google Docs or any external tools.
            """
        )
        
        compile_result: RunOutput = compile_report_task.run(input=f"Compile a research report about {topic} in the domain {domain}")
        st.session_state.report_content = compile_result.content
        st.session_state.research_complete = True
        
        # Save to history
        history_entry = {
            'topic': topic,
            'domain': domain,
            'timestamp': datetime.now().isoformat(),
            'question_count': len(question_answers),
            'report_content': compile_result.content
        }
        st.session_state.research_history.insert(0, history_entry)
        # Keep only last 10 entries
        if len(st.session_state.research_history) > 10:
            st.session_state.research_history = st.session_state.research_history[:10]
        
        return compile_result.content

# Export functions
def export_to_markdown(report_content, topic, domain):
    """Export report to Markdown format"""
    md_content = f"# Research Report: {topic}\n\n"
    md_content += f"**Domain:** {domain}\n\n"
    md_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += "---\n\n"
    # Basic HTML to markdown conversion (remove HTML tags)
    import re
    # Remove HTML tags but keep text content
    text_content = re.sub(r'<[^>]+>', '', report_content)
    # Clean up extra whitespace
    text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
    md_content += text_content
    return md_content

def export_to_json(question_answers, question_sources, topic, domain):
    """Export research data to JSON format"""
    data = {
        'topic': topic,
        'domain': domain,
        'timestamp': datetime.now().isoformat(),
        'questions': [
            {
                'question': qa['question'],
                'answer': qa['answer'],
                'sources': sources
            }
            for qa, sources in zip(question_answers, question_sources)
        ]
    }
    return json.dumps(data, indent=2)

def export_to_pdf(report_content, topic, domain):
    """Export report to PDF format"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"Research Report: {topic}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Domain
    domain_para = Paragraph(f"<b>Domain:</b> {domain}", styles['Normal'])
    story.append(domain_para)
    story.append(Spacer(1, 0.1*inch))
    
    # Date
    date_para = Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
    story.append(date_para)
    story.append(Spacer(1, 0.3*inch))
    
    # Convert HTML content to paragraphs (basic conversion)
    # Remove HTML tags for PDF
    import re
    text_content = re.sub(r'<[^>]+>', '', report_content)
    paragraphs = text_content.split('\n\n')
    
    for para in paragraphs:
        if para.strip():
            p = Paragraph(para.strip(), styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 0.1*inch))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Main application flow
if openai_api_key and serpapi_key:
    # Initialize agents
    llm, serpapi_key_val, perplexity_key = initialize_agents(openai_api_key, serpapi_key, perplexity_api_key)
    
    # Research History Sidebar
    if st.session_state.research_history:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📚 Research History")
        for idx, entry in enumerate(st.session_state.research_history[:5]):
            with st.sidebar.expander(f"{entry['topic'][:30]}..." if len(entry['topic']) > 30 else entry['topic']):
                st.write(f"**Domain:** {entry['domain']}")
                st.write(f"**Date:** {entry['timestamp'][:10]}")
                if st.button(f"Load", key=f"load_{idx}"):
                    st.session_state.current_topic = entry['topic']
                    st.session_state.current_domain = entry['domain']
                    st.rerun()
    
    # Main content area
    st.header("Research Topic")
    
    # Input fields
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input(
            "What topic would you like to research?", 
            placeholder="American Tariffs",
            value=st.session_state.current_topic
        )
    with col2:
        domain = st.text_input(
            "What domain is this topic in?", 
            placeholder="Politics, Economics, Technology, etc.",
            value=st.session_state.current_domain
        )
    
    # Question customization
    st.markdown("### ⚙️ Research Settings")
    col1, col2 = st.columns(2)
    with col1:
        question_count = st.slider("Number of Questions", min_value=3, max_value=10, value=5, step=1)
    with col2:
        question_type = st.selectbox(
            "Question Type",
            ["yes/no", "open-ended", "comparative", "analytical"],
            index=0
        )
    
    # Generate questions section
    if topic and domain and st.button("Generate Research Questions", key="generate_questions"):
        # Generate questions
        questions = generate_questions(llm, topic, domain, question_count, question_type)
        
        # Display the generated questions
        st.header("Research Questions")
        for i, question in enumerate(questions):
            st.markdown(f"**{i+1}. {question}**")
    
    # Research section - only show if we have questions
    if st.session_state.questions and st.button("Start Research", key="start_research"):
        st.header("Research Results")
        
        # Reset answers
        question_answers = []
        question_sources = []
        
        # Research questions in parallel
        with st.spinner("🔍 Researching questions in parallel..."):
            results = asyncio.run(
                research_questions_parallel(llm, serpapi_key_val, perplexity_key, topic, domain, st.session_state.questions)
            )
        
        # Process results
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (question, (answer, sources)) in enumerate(zip(st.session_state.questions, results)):
            # Update progress
            progress = (i + 1) / len(st.session_state.questions)
            progress_bar.progress(progress)
            status_text.text(f"Processing question {i+1} of {len(st.session_state.questions)}")
            
            question_answers.append({"question": question, "answer": answer})
            question_sources.append(sources)
            
            # Display the answer with sources
            with st.expander(f"Question {i+1}: {question}", expanded=(i == 0)):
                st.markdown(answer)
                
                if sources:
                    st.markdown("**Sources:**")
                    for source in sources[:5]:  # Show top 5 sources
                        st.markdown(f"- [{source['title']}]({source['url']})")
        
        progress_bar.empty()
        status_text.empty()
        
        # Store the answers
        st.session_state.question_answers = question_answers
        st.session_state.question_sources = question_sources
        st.session_state.current_topic = topic
        st.session_state.current_domain = domain
        
        st.success(f"✅ Research completed for {len(question_answers)} questions!")
        
        # Compile report button
        if st.button("Compile Final Report", key="compile_report"):
            report_content = compile_report(llm, topic, domain, question_answers, question_sources)
            
            # Display the report content
            st.header("Final Report")
            st.success("Your report has been compiled successfully!")
            
            # Export buttons
            st.markdown("### 📥 Export Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                md_content = export_to_markdown(report_content, topic, domain)
                st.download_button(
                    label="📄 Download Markdown",
                    data=md_content,
                    file_name=f"research_report_{topic.replace(' ', '_')}.md",
                    mime="text/markdown"
                )
            
            with col2:
                json_content = export_to_json(question_answers, question_sources, topic, domain)
                st.download_button(
                    label="📊 Download JSON",
                    data=json_content,
                    file_name=f"research_data_{topic.replace(' ', '_')}.json",
                    mime="application/json"
                )
            
            with col3:
                pdf_buffer = export_to_pdf(report_content, topic, domain)
                st.download_button(
                    label="📑 Download PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"research_report_{topic.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            
            # Show the full report content
            with st.expander("View Full Report Content", expanded=True):
                st.markdown(report_content)
    
    # Display previous results if available
    if len(st.session_state.question_answers) > 0 and not st.session_state.research_complete:
        st.header("Previous Research Results")
        
        # Display research results
        for i, qa in enumerate(st.session_state.question_answers):
            with st.expander(f"Question {i+1}: {qa['question']}"):
                st.markdown(qa['answer'])
                if i < len(st.session_state.question_sources) and st.session_state.question_sources[i]:
                    st.markdown("**Sources:**")
                    for source in st.session_state.question_sources[i][:5]:
                        st.markdown(f"- [{source['title']}]({source['url']})")
    
    # Display final report if available
    if st.session_state.research_complete and st.session_state.report_content:
        st.header("Final Report")
        
        # Display the report content
        st.success("Your report has been compiled successfully!")
        
        # Export buttons
        if st.session_state.current_topic and st.session_state.current_domain:
            st.markdown("### 📥 Export Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                md_content = export_to_markdown(st.session_state.report_content, st.session_state.current_topic, st.session_state.current_domain)
                st.download_button(
                    label="📄 Download Markdown",
                    data=md_content,
                    file_name=f"research_report_{st.session_state.current_topic.replace(' ', '_')}.md",
                    mime="text/markdown",
                    key="export_md_final"
                )
            
            with col2:
                json_content = export_to_json(st.session_state.question_answers, st.session_state.question_sources, st.session_state.current_topic, st.session_state.current_domain)
                st.download_button(
                    label="📊 Download JSON",
                    data=json_content,
                    file_name=f"research_data_{st.session_state.current_topic.replace(' ', '_')}.json",
                    mime="application/json",
                    key="export_json_final"
                )
            
            with col3:
                pdf_buffer = export_to_pdf(st.session_state.report_content, st.session_state.current_topic, st.session_state.current_domain)
                st.download_button(
                    label="📑 Download PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"research_report_{st.session_state.current_topic.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key="export_pdf_final"
                )
        
        # Show the full report content
        with st.expander("View Full Report Content", expanded=True):
            st.markdown(st.session_state.report_content)

else:
    # API keys not provided
    st.warning("⚠️ Please enter your OpenAI API key and SerpApi key in the sidebar to get started. Perplexity API key is optional.")
    
    # Example UI
    st.header("How It Works")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("1️⃣ Define Topic")
        st.write("Enter your research topic and domain to begin the research process.")
    
    with col2:
        st.subheader("2️⃣ Generate Questions")
        st.write("The AI generates specific research questions to explore your topic in depth.")
        
    with col3:
        st.subheader("3️⃣ Compile Report")
        st.write("Research findings are compiled into a professional report with export options.")
