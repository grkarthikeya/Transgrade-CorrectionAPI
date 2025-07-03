# from crewai import Agent, Crew, Process, Task
# from crewai.project import CrewBase, agent, crew, task
# from crewai.agents.agent_builder.base_agent import BaseAgent
# from typing import List
# # If you want to run a snippet of code before or after the crew starts,
# # you can use the @before_kickoff and @after_kickoff decorators
# # https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# @CrewBase
# class OcrCorrection():
#     """OcrCorrection crew"""

#     agents: List[BaseAgent]
#     tasks: List[Task]

#     # Learn more about YAML configuration files here:
#     # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
#     # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
#     # If you would like to add tools to your agents, you can learn more about it here:
#     # https://docs.crewai.com/concepts/agents#agent-tools
#     @agent
#     def answer_segmenter(self) -> Agent:
#         return Agent(
#             config=self.agents_config['answer_segmenter'], # type: ignore[index]
#             verbose=True
#         )

#     @agent
#     def ocr_word_validator(self) -> Agent:
#         return Agent(
#             config=self.agents_config['ocr_word_validator'], # type: ignore[index]
#             verbose=True
#         )
    
#     @agent
#     def word_corrector(self) -> Agent:
#         return Agent(
#             config=self.agents_config['word_corrector'], # type: ignore[index]
#             verbose=True
#         )
   

    


#     # To learn more about structured task outputs,
#     # task dependencies, and task callbacks, check out the documentation:
#     # https://docs.crewai.com/concepts/tasks#overview-of-a-task
#     @task
#     def segment_answers(self) -> Task:
#         return Task(
#             config=self.tasks_config['segment_answers'], # type: ignore[index]
#         )


#     @task
#     def detect_word_issues(self) -> Task:
#         return Task(
#             config=self.tasks_config['detect_word_issues'], # type: ignore[index]
#         )
    
#     @task
#     def correct_words_using_context(self) -> Task:
#         return Task(
#             config=self.tasks_config['correct_words_using_context'], # type: ignore[index]
#         )


    
        
        
#     @crew
#     def crew(self) -> Crew:
#         """Creates the OcrCorrection crew"""
#         # To learn how to add knowledge sources to your crew, check out the documentation:
#         # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

#         return Crew(
#             agents=self.agents, # Automatically created by the @agent decorator
#             tasks=self.tasks, # Automatically created by the @task decorator
#             process=Process.sequential,
#             verbose=True,
#             # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
#         )


# from crewai import Agent, Crew, Process, Task
# from crewai.project import CrewBase, agent, crew, task
# from crewai.agents.agent_builder.base_agent import BaseAgent
# from typing import List

# @CrewBase
# class Correction():
#     """OCR Error Correction crew"""

#     agents: List[BaseAgent]
#     tasks: List[Task]

#     @agent
#     def ocr_corrector(self) -> Agent:
#         return Agent(
#             config=self.agents_config['ocr_corrector'], # type: ignore[index]
#             verbose=True
#         )

#     @task
#     def ocr_correction_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['ocr_correction_task'], # type: ignore[index]
#             output_file='corrected_ocr.json'
#         )

#     @crew
#     def crew(self) -> Crew:
#         """Creates the OCR Correction crew"""
#         return Crew(
#             agents=self.agents, # Automatically created by the @agent decorator
#             tasks=self.tasks, # Automatically created by the @task decorator
#             process=Process.sequential,
#             verbose=True,
#         )


from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Correction():
    """OcrCorrection crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def parser_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['parser_agent'], # type: ignore[index]
            verbose=True
        )

    @agent
    def comparison_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['comparison_agent'], # type: ignore[index]
            verbose=True
        )
        
    @agent
    def logger_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['logger_agent'], # type: ignore[index]
            verbose=True
        )
        
    @agent
    def report_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['report_agent'], # type: ignore[index]final_corrector_agent
            verbose=True
        )

    @agent
    def final_corrector_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['final_corrector_agent'], # type: ignore[index]final_corrector_agent
            verbose=True
        )

    # @agent
    # def restructuring_agent(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['restructuring_agent'], # type: ignore[index]final_corrector_agent
    #         verbose=True
    #     )


    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def ocr_parser_task(self) -> Task:
        return Task(
            config=self.tasks_config['ocr_parser_task'], # type: ignore[index]
        )

    @task
    def ocr_comparison_task(self) -> Task:
        return Task(
            config=self.tasks_config['ocr_comparison_task'], # type: ignore[index]
            output_file='report.md'
        )
    
    @task
    def ocr_logging_task(self) -> Task:
        return Task(
            config=self.tasks_config['ocr_logging_task'], # type: ignore[index]
            output_file='report.md'
        )
    
    @task
    def ocr_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['ocr_report_task'], # type: ignore[index]
            output_file='report.md'
        )

    @task
    def final_output_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_output_task'], # type: ignore[index]
            output_file='report.md'
        )

    # @task
    # def restructure_corrected_outputs_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['restructure_corrected_outputs_task'], # type: ignore[index]
    #         output_file='report.md'
    #     )
        
        
    @crew
    def crew(self) -> Crew:
        """Creates the OcrCorrection crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )