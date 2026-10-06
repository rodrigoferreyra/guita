# Software Product Documentation Style Guide

## Information Architecture

The knowledge base should be organized with a clear structure that separates informative, instructional, and agent-based configuration content for an optimal user experience.

This section outlines how to structure the information within the knowledge base and best practices.

### Distinguishing content type

Technical content is categorized into four core topic types:

**Informative/conceptual content:** Provides background information and explains the purpose or functionality of a feature or task. It answers the question “what is it? What does it do? How does it fit within the system?”

**Instructional/task content:** Provides instructions on how to use a feature or perform a task. It answers the question “how do I do it?”

**Reference/database content:** Provides reference information which readers query on quick look-up. This includes structured facts such as object properties, command syntax, API references, or property tables.

**Agent Instruction content:** Defines the behaviors, constraints, goals, and logic required to build and customize AI agents. It answers the question "how do I configure an AI agent to execute this job reliably?"

### Organizing content

These content types should be separated. Separating content makes it easier for users to find what they need. Users looking for a quick overview of the product or feature can find the informative content, while those who require specific instructions can easily locate them. Separating content types avoids overwhelming users with too much information at once. Try to keep informative content outside instructional content, since it is harder to find for those who are not looking to see how to do something, but understand a feature.

To separate content:

**Start with informative content:** Begin by explaining the feature’s purpose and benefits. This context helps users understand why a feature exists before they dive into how to use it.

**Follow with instructional content:** Once users have a foundational understanding of a feature, focus on guiding users through specific tasks. To this end, provide clear step-by-step instructions on how to use the feature.

**Include reference content where applicable:** Ideally, reference content should be at reach after its dependent concept has been introduced. This is where readers expect references at, and proximity allows them to quickly see how to extend the actions they want to perform.

While content should be divided by its nature, it should not be addressed as such. Do not label sections as informative, instructional, or similar. Reference may be used as a heading when that is the natural name for a lookup section.

## Writing informative content

**Start with foundational concepts:** Begin by introducing core functionalities and basic features. Additional configurations should go last.

**Sentence & paragraph structure:** Use concise sentences of moderate length. If the subject demands complexity, divide information into sentences. Likewise, if information start revolving around more than one concept, separate sentences into paragraphs. As a mnemotechnic, think of paragraphs as the minimal unit of meaning.

**Headings and subheadings:** Use descriptive headings and subheadings to help users navigate the content and locate specific information.

**Anticipate user needs:** Consider potential user questions and proactively address them within the content.

**Provide context:** Provide enough context for each topic to ensure users with varying levels of knowledge or familiarity with the product can understand the information.

**Break down content into modules:** Structure the knowledge base into manageable sections. This modular approach helps users to screen for what they need and writers to maintain the documentation.

**Link-related articles:** Strategically use cross-linking to connect related articles within the knowledge base. This helps users discover additional context and navigate to relevant information. However, prioritize keeping essential information in a single page to minimize the need for excessive navigation.

**Provide context:** Each article must within its first paragraph provide enough context so readers known if they page has the information they were looking for or not.

## Writing instructional content

**Numbering steps:** Numbering steps in instructional content makes it easier for users to follow the process. If a process takes more than 5 steps, consider breaking it down into more than one process.

**Bad:** “To create a new campaign, enter the campaign name, description, start date, and end date. Then choose the target audience and budget.” (Long sentence)

**Good:** “To create a new campaign:

1. Enter the campaign name, description, start date, and end date.

2. Choose the target audience.

3. Set the budget.”

When providing instructions, you will need to refer to the UI. To do so, use the correct term for UI elements. Try to be as specific as possible. There are multiple lists of terminology for UI elements. Use an established UI terminology reference when appropriate.

**Bad:** “Click the gear icon in the top right corner to access your settings.” (“Gear icon” might not be universally understood)

**Good:** “Click the Settings icon (gear icon) in the top right corner to access your settings.” (Clarifies the icon with a common term in parentheses)

**Bad:** “Enter your search query in the search bar at the top of the page.” (“Search bar” is widely understood, but there could be confusion)

**Good:** “In the search field located at the top of the page, enter your search query.” (“Search field” is a more specific term for the UI element)

**Bad:** “To create a new report, click the plus button next to the ‘Reports’ tab.” (“Plus button” might be vague)

**Good:** “To create a new report, click the ‘New Report’ button located next to the ‘Reports’ tab.” (Uses the specific button label)

**Bad:** “Use the slider to adjust the volume level.” (“Slider” is appropriate, but consider adding context)

**Good:** “Using the volume control slider, adjust the volume level to your preference.” (Provides context for the UI element)

Use bold on UI element names.

Do not use a table of contents. If the content is too large for a single page, create another document.

## Subheading types

Depending on the nature of the content, it can be organized under different thematic subheadings:

**How it works:** Explains how the feature functions within the product.

**Key features:** In the case of a product or feature with multiple actions, it lists its features or actions with a brief overview of each.

**Main benefits:** In the case of a product or prominent feature, it showcases its trade-offs.

**Agent Blueprint:** Defines the baseline operational role, constraints, and instructions required to program an AI agent for the feature.

## Formatting & Visuals

Follow formatting guidelines to ensure the knowledge base content is visually appealing, easy to understand, and consistent across all articles.

Use consistent capitalization.

Only use title capitalization for page titles, not for subheadings.

Use bullet points to present lists of features or benefits. Use numbered lists for steps.

Use descriptive link text instead of just URLs. The descriptive text helps users understand where the link leads before they click.

Bold must be used when introducing important keywords, product concepts, and objects and fields.

Italics must be used for information within fields or options. Italics can also be used for foreign words or placeholders.

## Visual elements

## Branding guidelines & assets

This section provides a summary of the branding guidelines most relevant to the knowledge base. The complete brand guidelines should be available to documentation contributors. Branding assets should likewise be maintained in an accessible location for the documentation team.

### Brand overview

**Primary brand:** Product brand

**Design principle:** Clean, modern, and integrated visual system.

## Why use visuals?

Visuals draw the reader's eye and act as focal points within a text-heavy document.

Complex concepts can be grasped instantly through well-designed visuals.

By simplifying information, visuals lessen the mental effort required to process content.

People retain information presented visually better than text alone.

## When to place visuals

To introduce a topic with a relevant diagram or illustration to prime the reader.

To clarify processes or complex ideas throughout the explanation.

In the case of screenshots, to showcase specific steps involved in completing a task.

## Creating visuals

Focus on conveying the core concept through simple shapes and clear lines. Avoid excessive detail that might distract from the message.

Ensure visuals directly relate to the surrounding text and effectively communicate the intended meaning.

Remove unnecessary elements that don't contribute to understanding.

Simple line drawings are often more effective than detailed illustrations. The challenge lies in translating the idea into a visual form, not artistic perfection.

Use a consistent visual style throughout your documentation for a polished look.

Use platform visual elements to organize content. In the case of a documentation platform, you can use different blocks such as callouts as visual aids in your content. See the platform's documentation on how to use the editor.

## Callouts

Use documentation-platform callouts for brief pieces of information that you want to stand out:

:::hint{type="info"} Info: Information that is important to understand the product, optimize agent system performance, or set it up correctly. :::

:::hint{type="success"} Success: Communicate best practices, prompt optimization tips, or successful configuration metrics. :::

:::hint{type="warning"} Warning: Information users should pay attention to in order for the product or the AI workflow handoffs to work as expected when performing an action. :::

:::hint{type="danger"} Danger: Information that, if ignored, could break configurations, result in agent misalignment, or disrupt production data. :::

In plain Markdown repositories without that callout syntax, prefer a short bold lead-in such as **Note:** or **Warning:** instead of inventing custom HTML.

## User Assumptions

**Key takeaway:** In terms of the user's knowledge level, the knowledge base should strike a balance between providing clear instructions and acknowledging users with some platform and AI configuration experience.

### Baseline knowledge

The knowledge base prioritizes functionality, offering clear and concise instructions for completing tasks within the platform. However, it also provides depth for various use cases to cover products’ entire functionalities. This section helps you understand the user’s knowledge level to target the content appropriately.

In essence, if we assume a certain level of user knowledge, we can choose to skip explanations to varying degrees. In this regard, this knowledge base assumes users possess a fundamental understanding of core platform concepts and basic AI agent architecture, including:

**Platform interface:** Familiarity with the application interface, including navigation elements such as tabs, objects, fields, records, and other common UI elements. Users might be unfamiliar with legacy interfaces, so pay closer attention to explaining them.

**Data management:** Basic understanding of creating, editing, and deleting data within the application.

**Reports and dashboards:** Ability to access and navigate reports and dashboards to view and analyze data.

**Basic application workflows and processes:** General knowledge of how workflows and processes can automate tasks and enforce business logic within the application.

**Product documentation:** Familiarity with the product's resources for learning how to use the platform.

**Product terminology:** Knowledge of product terminology, such as objects and field types, as well as feature-specific concepts and functionalities.

**Agent Customization:** Conceptual awareness of how AI agents interpret goals, use integrated tooling, execute conditional handoffs via triggers, and adopt designated personas.

Based on these baseline knowledge assumptions:

Users should be able to figure out how to tweak some functionalities, so it’s not necessary to cover every possible scenario. You can still mention the ability to customize features, but only provide detailed explanations in specific cases, such as highly valuable features. For these features, you can include instructions on configuring the application to achieve the desired outcome.

Users should be able to navigate the platform to learn how to do something on their own. Therefore, in many cases, you can direct them to a relevant product documentation entry instead of writing a full tutorial.

However, we acknowledge there might be users who are less technical and need more help with basic platform or prompt-engineering tasks. The knowledge base should prioritize functionality but also provide depth for different use cases and cover the entire range of the platform’s functionalities. As such, the knowledge base should cater to these users as well by providing readily available links to connect with customer service.

For Guita, assume the reader is comfortable with a terminal, Python virtual environments, and basic command-line usage.

## Voice and Tone

This section defines the desired communication style for the knowledge base. As such, it will detail the overall personality of the knowledge base and how it reflects the brand as well as the nuances for specific situations.

The knowledge base should strive for a consistent voice and tone that is clear, concise, and action-oriented. It should combine friendliness and professionalism, ensuring information is comprehensive and users feel supported.

### Key principles (dos)

**Clarity and conciseness:** Prioritize using straightforward language and simple sentence structure. Break down complex information into easy-to-understand steps. If a sentence is too long or has many ideas, try to break it into sentences.

**Good:** “The application is an equipment location and inventory management system.” (Clear and concise definition)

**Bad:** “The system is a multifaceted application within the platform that serves the purpose of equipment location tracking and inventory management.” (Unnecessary complexity)

**Courtesy and professionalism:** Explain information with the goal of helping the user. In like manner, don’t assume or point out user error.

**Good:** “If you encountered an error while creating reports in the application, here are some common issues and steps you can try.” (Empathetic and helpful, specific to reports)

**Bad:** “If your reports aren’t working in the application, you must be doing something wrong. Make sure you follow these steps exactly.” (Impatient and accusatory, assumes user error)

**Good:** “If you encounter issues logging in to the application, there are a few steps you can try to troubleshoot the problem. First, double-check that you’ve entered the correct username and password. If the issue persists, you can reset your password using the ‘Forgot Password’ link on the login page. As a last resort, you can contact support for further assistance.”

**Bad:** “If you’re having trouble logging in to the application, check your username and password. If that doesn’t work, reset your password. You can also contact support for further assistance.”

**Active voice:** Active voice prioritizes clarity and engagement by focusing on the subject performing the action. Sentences written in an active voice are generally easier to understand.

**Example (Active Voice):** “Create a new report by clicking the ‘Reports’ tab and selecting ‘New Report’.” (Focuses on the user and the action of creating a report)

While active voice is generally preferred, there are a few situations where passive voice might be acceptable:

**Emphasis on the object:** When you want to emphasize the object receiving the action, passive voice can be a good choice.

**Unknown subject:** If the subject performing the action is unknown or unimportant, passive voice can be used.

**Example (Passive Voice - Acceptable):** “Errors are sometimes encountered when creating reports in the application.” (Here, the emphasis is on the errors encountered, not necessarily the user creating the report) It’s important to use your judgment and choose the voice that best conveys the intended meaning and clarity for the user.

**Direct address:** Address the reader directly using the second-person pronoun (“you”). Never address the reader using the first-person plural. As such, avoid pronouns like “we” or “us” that imply a collective action.

**Good:** “You can customize your notification preferences by clicking on the bell icon in the top right corner.” (Speaks directly to the reader)

**Good:** “The notification preferences can be customized by clicking on the bell icon in the top right corner.” (Impersonal but acceptable)

**Bad:** “Let’s navigate to the Accounts tab…” (Incorrect - First-person plural)

**Technical depth:** The knowledge base should be complete enough that the user is confident to use it as a complete source of truth on how to use a product or build its related AI instructions. When a subject goes beyond the scope of a section of the knowledge base (as specified in the User Assumptions section), users should receive assistance to find the information they need.

**Good:** “For advanced configuration options, please refer to the system administrator guide.” (Guides users for further details)

**Bad:** “This feature allows for advanced configuration, but we won’t cover it here.” (Incomplete information, leaves user unsure)

Test your instructions to ensure they work and are easy to follow. This applies equally to documentation steps and prompt-based agent guidelines.

**Consistent terminology:** Use the same term consistently across all documentation for a specific feature or concept to avoid confusing the reader.

Introduce and define abbreviations within the text the first time they are used and on each page.

Use transition words to improve readability. Ensure the words you choose reflect the relationship between the ideas they connect.

### What to avoid (don’ts)

Internet abbreviations, slang, and exclamation marks.

**Bad:** “Let’s add a new contact ASAP!” (Uses “Let’s” - first-person plural - and “ASAP” - internet abbreviation)

**Good:** “Navigate to the Contacts tab and click ‘New Contact’ to add a new contact.” (Clear instruction, no slang)

Categorizing how complex a procedure is and using terms like “easy” or “simple”.

**Bad:** “This is an easy procedure, just follow these steps…” (Avoids labeling complexity)

**Good:** “Follow these steps to add a new product to your inventory.” (Neutral and to the point)

Unnecessary jargon or unnecessary embellishment.

**Bad:** “Intuitively navigate to the ‘Contacts’ tab and utilize the ‘New Contact’ button to effortlessly add a new contact.” (Uses unnecessary adverbs like “intuitively” and “effortlessly”)

**Good:** “Go to the ‘Contacts’ tab and click ‘New Contact’ to add a new contact.” (Direct and to the point, removes unnecessary adverbs)

Putting content as coming from your own experience. A knowledge base should be a reliable source of factual information, not personal anecdotes. While your experience might be valuable, it’s not guaranteed to be universally applicable for all users.

**Bad:** “In my experience, using a descriptive subject line for your emails will significantly improve your response rate. Here’s how to create one…” (This injects personal experience and doesn’t represent a universal fact)

**Bad:** “I always found it helpful to break down complex reports into smaller sections. Here are some tips…” (Focuses on the writer’s preference, not necessarily the best approach)

**Good:** “Breaking down complex reports into smaller sections can be a useful strategy for better understanding. Here are some tips for doing this…” (Focuses on the strategy itself and its benefits)

Gendered language.

### Job titles

**Bad:** “The salesman will contact you after reviewing your lead.” (Gendered job title)

**Good:** “The sales representative will contact you after reviewing your lead.” (Gender-neutral job title)

**Bad:** “The fireman should be called in case of a fire.” (Gendered job title)

**Good:** “The firefighter should be called in case of a fire.” (Gender-neutral job title)

### Pronouns

**Bad:** “If a customer has a question, he can contact support.” (Assumes customer is male)

**Good:** “If a customer has a question, they can contact support.” (Gender-neutral pronoun)

**Bad:** “Her manager will be happy to answer any questions.” (Assumes manager is female)

**Good:** “The manager will be happy to answer any questions.” (Avoids assuming gender)

### “He/she” construction

**Bad:** “The administrator logs in to the system and selects his/her preferences.” (Awkward and repetitive)

**Good:** “Administrators log in to the system and select their preferences.” (Singular becomes plural, avoids gendered pronoun)

Metaphors. However, you can use analogies if the concept is too complex. Still, try to remain within the domain of the product.

**Metaphor (Bad):** “Understanding user permissions in an application is like juggling different colored balls. Each ball represents a permission level, and you need to keep them all in the air to ensure users have the right access.” (Metaphor might be unclear for some users)

**Analogy within the product domain (Good):** “Understanding user permissions in an application is similar to assigning different access levels to rooms in a building. An ‘admin’ has a master key that opens all doors, while a ‘standard user’ might only have access to specific rooms based on their assigned permissions.” (Analogy uses familiar concepts related to the product—user roles and access)

Localisms, idioms, and terms that might be confusing for non-native speakers. Aim for international audiences.

**Bad:** “Don’t drop the ball on this important task! Make sure you complete it on time.” (“Drop the ball” is an idiom not understood by everyone)

**Good:** “It’s important to prioritize this task and ensure it’s completed by the deadline.” (Replaces the idiom with a clear instruction)

**Bad:** “Make sure you have the ‘NIF’ number for your customer in Spain.” (“NIF” is a Spanish tax identification number, not universally known)

**Good:** “In Spain, you’ll need your customer’s ‘Tax Identification Number’ (TIN) for billing purposes.” (Defines the term for clarity)

Technical terms that are not relevant to the domain.

Ambiguous terminology.

**Bad:** “After you’ve ‘flagged’ a report, it will be sent to your manager for review.” (“Flagged” can have different meanings depending on location)

**Good:** “Once you’ve marked a report for ‘review,’ it will be sent to your manager.” (Uses a clear and official term for the action)
