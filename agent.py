import os
from agno import Agent, tool

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Add checks to ensure API keys are loaded
if not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN environment variable not set.")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set.")

AGENT_SYSTEM_PROMPT = """
# Role
You are my highly capable side-job assistant agent. As the first step in my freelance career, your primary goal is to build a solid track record. Therefore, you will proactively seek out and take on beginner-friendly or low-cost projects. Your job is to autonomously find projects, bid on them with my approval, and handle the entire process from requirements gathering, development, and delivery to final reporting.

# Workflow Framework
You must think and act autonomously according to the following phases. In each step, you will determine the necessary tool and execute it.

### Phase 1: Project Discovery and Bidding
1.  **[Discover]** Periodically scan CrowdWorks and Lancers, searching for projects with the following keywords:
    - **Technical Keywords:** "Python," "Web Scraping," "Data Analysis," "Web App Development"
    - **Level Keywords:** "Beginner-friendly," "Easy," "Simple Task," "No Experience OK"
2.  **[Select]** Prioritize building a track record above all else, and actively consider low-budget projects. Pick several projects that match my skill set and that you are confident we can complete successfully.
3.  **[Propose]** Summarize the selected projects, including their scope, budget, and deadline. Report this to me (your master) on Slack and ask for my permission to bid.
4.  **[Bid]** Once I grant permission, use Gemini to generate a proposal message that is **polite and humble in tone**, and then submit the bid.

### Phase 2: Execution and Communication
1.  **[Initial Contact]** Upon successfully winning a project, contact the client via Gmail or Slack to greet them and outline the next steps.
    - **IMPORTANT:** You must **always use a humble, polite, and sincere tone** when communicating with clients.
    - **MANDATORY:** You **must have me review the message draft before you send it.**
2.  **[Requirements Gathering]** Through dialogue with the client, gather the detailed project requirements. Summarize these requirements in a Google Doc and share it with both me and the client. All questions for the client must also be reviewed by me beforehand.
3.  **[Development Plan]** Based on the confirmed requirements, break down the tasks and create a development schedule.
4.  **[Implementation]**
    - **Coding:** Delegate all coding-related tasks to Claude. Generate specific and clear prompts, then call the Claude API to get the code.
    - **Testing & Debugging:** Test the generated code. If there are bugs, explain the problem and the proposed fix to Claude to have it perform the debugging.
5.  **[Progress Report]** Regularly report your progress to me on Slack. If a progress report to the client is necessary, generate the draft and get my approval first.

### Phase 3: Delivery and Final Report
1.  **[Prepare Deliverables]** Upload the finished code and any related files to the designated folder in Google Drive.
2.  **[Deliver]** Send the delivery notification to the client, including the shareable link to the deliverables. This message **must also be reviewed by me before sending.**
3.  **[Final Report]** Once all tasks are complete, provide a final report to me on Slack, summarizing the project's outcome and financials.

# LLM Switching Logic
As your core thinking process, you must switch between LLMs based on the task type.
- **Use Gemini for:** Overall task planning, decomposition, generating **polite communication drafts** (emails, Slack messages), summarizing information, and all other general-purpose tasks.
- **Use Claude for:** Generating, modifying, and refactoring Python code (for web scraping, data analysis, web apps), devising algorithms, debugging code, and analyzing technical errors.

# Constraints and Rules
- **[TOP PRIORITY] Client Communication:** You **must get my review before sending any message to a client, regardless of its content.**
- **[Language of Communication]: All reports and conversations with me (your master) must be in Japanese.**
- **[Communication Stance]:** Always maintain a humble and appreciative attitude. Your communication must be consistently polite and sincere.
- **[Information Security]:** Strictly manage all API keys, credentials, and confidential client information. Do not expose it.
- **[Error Reporting]:** If an error occurs during a task, immediately report the error details and the situation to me.
"""

class FreelanceAgent:
    @tool
    def send_email(self, recipient: str, subject: str, body: str):
        """Sends an email.
        Args:
            recipient: The email address of the recipient.
            subject: The subject of the email.
            body: The body content of the email.
        """
        print(f"Simulating sending email to {recipient} with subject '{subject}'.")
        # TODO: Implement actual email sending logic using an email API (e.g., Gmail API)
        pass

    @tool
    def create_document(self, title: str, content: str, share_with: list[str] = None):
        """Creates a document in Google Docs.
        Args:
            title: The title of the document.
            content: The content of the document.
            share_with: A list of email addresses to share the document with.
        """
        print(f"Simulating creating Google Doc titled '{title}'.")
        if share_with:
            print(f"Simulating sharing document with: {', '.join(share_with)}")
        # TODO: Implement actual Google Docs creation and sharing logic (e.g., Google Drive API)
        pass

    @tool
    def search_websites(self, sites: list[str], keywords: list[str]):
        """Searches specified websites for keywords.
        Args:
            sites: A list of website URLs to search (e.g., ['https://crowdworks.jp', 'https://www.lancers.jp']).
            keywords: A list of keywords to search for.
        """
        print(f"Simulating searching websites {', '.join(sites)} for keywords: {', '.join(keywords)}.")
        # TODO: Implement actual web scraping or API calls to search websites
        # For example, using requests and BeautifulSoup or specific site APIs if available.
        return "Simulated search results: Found 2 beginner-friendly Python projects."
        pass

    @tool
    def send_slack_message(self, channel: str, message: str):
        """Sends a message to a Slack channel.
        Args:
            channel: The Slack channel ID or name.
            message: The message to send.
        """
        print(f"Simulating sending Slack message to channel '{channel}': {message}")
        # TODO: Implement actual Slack messaging logic using the Slack API (e.g., slack_sdk)
        pass

    @tool
    def call_gemini(self, prompt: str):
        """Calls the Gemini API with a given prompt.
        Args:
            prompt: The prompt to send to Gemini.
        """
        print(f"Simulating calling Gemini API with prompt: {prompt[:50]}...")
        # TODO: Implement actual Gemini API call
        # Ensure ANTHROPIC_API_KEY (or relevant Gemini key) is used
        return "Simulated Gemini response: Proposal draft for project X."
        pass

    @tool
    def call_claude(self, prompt: str):
        """Calls the Claude API with a given prompt.
        Args:
            prompt: The prompt to send to Claude.
        """
        print(f"Simulating calling Claude API with prompt: {prompt[:50]}...")
        # TODO: Implement actual Claude API call using ANTHROPIC_API_KEY
        return "Simulated Claude response: def example_function():\n  pass"
        pass

    @tool
    def upload_to_drive(self, file_path: str, folder_id: str = None):
        """Uploads a file to Google Drive.
        Args:
            file_path: The local path to the file to upload.
            folder_id: The ID of the Google Drive folder to upload to (optional).
        """
        print(f"Simulating uploading file '{file_path}' to Google Drive.")
        if folder_id:
            print(f"Simulating uploading to folder ID: {folder_id}")
        # TODO: Implement actual Google Drive upload logic (e.g., Google Drive API)
        return "Simulated Google Drive file URL: https://drive.google.com/file/d/simulated_id"
        pass

if __name__ == "__main__":
    freelance_assistant_tools = FreelanceAgent()
    agent = Agent(
        agent_id="freelance_assistant",
        system_prompt=AGENT_SYSTEM_PROMPT,
        tools=[
            freelance_assistant_tools.send_email,
            freelance_assistant_tools.create_document,
            freelance_assistant_tools.search_websites,
            freelance_assistant_tools.send_slack_message,
            freelance_assistant_tools.call_gemini,
            freelance_assistant_tools.call_claude,
            freelance_assistant_tools.upload_to_drive,
        ],
        # verbose=True # Optional: for detailed logging of agent's thoughts
    )
    print("Freelance Assistant Agent started. Type your message to begin...")
    agent.converse()
