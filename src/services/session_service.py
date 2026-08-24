# from src.enums.chatbot_type_enum import ChatbotTypeEnum
from src.enums.chatbot_type_enum import ChatbotTypeEnum
from src.exception.user_exception import ExceptionUserNotFound
from src.configs import settings
from src.enums.user_role_enum import UserRole
from src.models.task.response.task_response_model import TaskResponse
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.repositories.session.session_repository import SessionRepository
from src.models.session.request.filter_session_model import FilterSessionModel, FilterCheckInSessionModel, \
    FilterSessionByDateRangeModel
from src.models.session.request.update_session_model import UpdateSessionModel, CheckoutModel, UpdateSubTaskModel, \
    CheckoutComgaoModel
from src.models.session.request.create_session_model import CreateSessionModel, CreateSessionComgao
from src.models.session.response.session_response_model import SessionResponse, SessionTaskResponse
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.exception.session_exception import SessionException, SessionMessage, SessionStatusCode
from src.exception.task_exception import TaskException, TaskStatusCode, TaskMessage
from src.enums.work_item_type import WorkItemType
from src.enums.task_status_enum import TaskStatusEnum
from src.models.task.request.update_task_model import UpdateTaskModel
from datetime import datetime
from src.utils.datetime_util import DateTimeUtil
from src.repositories.user.user_repository import UserRepository
from src.repositories.chatbot_token.chatbot_token_repository import ChatbotTokenRepository
from src.repositories.department.department_repository import DepartmentRepository
from src.models.department.request.filter_department_model import FilterDepartmentModel
from src.models.chatbot_token.request.filter_chatbot_token_model import FilterChatbotTokenModel
from src.utils.google_chat_webhook_util import GgChatWebhookUtil
from src.utils.form_text_gg_chat_api import FormatContentGgChatAPI
import asyncio
from zoneinfo import ZoneInfo
from fastapi import BackgroundTasks
import math
from src.enums.session_status_enum import SessionStatusEnum
import logging
logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self, session_repository: SessionRepository, work_item_repository: WorkItemRepository,
                 chatbot_token_repository: ChatbotTokenRepository, user_repository: UserRepository,
                 department_repository: DepartmentRepository,
                 ):
        self.session_repository = session_repository
        self.work_item_repository = work_item_repository
        self.chatbot_token_repository = chatbot_token_repository
        self.user_repository = user_repository
        self.department_repository = department_repository

    async def create_session(self, session_data: CreateSessionModel) -> ResponseModel:
        # check has session in today has not done

        await self.check_user_checkin(session_data.user_id)
        # check status
        new_session = await self.session_repository.create_session(session_data.model_dump())
        logger.info('checkin success with data: %s',new_session)
        created_session = await self.session_repository.get_session_by_id(str(new_session.id))
        response = SessionResponse.model_validate(created_session)
        # inject call webhook
        # get token
        filter_chat_token_master = FilterChatbotTokenModel(offset=0, limit=1, type=[ChatbotTypeEnum.MASTER.value])
        departments = [f"DEPARTMENT_{department}" for  department in response.user.department] if response.user.department else []
        filter_chat_token = FilterChatbotTokenModel(offset=0, limit=100, position=departments, type=[ChatbotTypeEnum.DEFAULT])
        # print("filter_chat_token : ",filter_chat_token)

        chat_token, total = await self.chatbot_token_repository.get_list_chatbot_tokens(filter_chat_token)
        token_master, total_master = await self.chatbot_token_repository.get_list_chatbot_tokens(filter_chat_token_master)

        chat_token.extend(token_master)
        print("chat token", chat_token)
        # print("chat_token : ",chat_token)
        if total+ total_master > 0:
            list_task = []
            list_task_data = []
            await asyncio.gather(*[
                self.get_work_item_by_id(work_id, list_task, list_task_data)
                for work_id in session_data.list_task
            ])
            # get department data
            departments = None
            if response.user and response.user.department:
                filter_depart = FilterDepartmentModel(offset=0, limit=len(response.user.department),
                                                      list_ids=response.user.department)
                departments, total = await self.department_repository.get_list_departments(filter_depart)
                if total:
                    departments = [department.name for department in departments]
                else:
                    departments = None
            content = FormatContentGgChatAPI.format_content_checkin(response.user.name, list_task,session_data.notes, departments, session_data.start_time, response.user.nickname, session_data.checkin_late, session_data.arrival_status, session_data.work_form)
            for token in chat_token:
                GgChatWebhookUtil.call_webhook(content, token.space_id, token.key, token.token)
            response.list_tasks_data = list_task_data
        return ResponseModel(data=response)

    async def update_session(self, session_id:str, session_data: UpdateSessionModel, user_id:str) -> ResponseModel:
        session = await self.session_repository.get_session_by_id(session_id)
        if not session:
            raise SessionException(SessionMessage.NOT_FOUND, SessionStatusCode.NOT_FOUND)
        logger.info('session : %s',session)
        logger.info('session update success with data: %s',session_data.model_dump(exclude_unset=True))
        if user_id != session.user_id:
            raise SessionException(SessionMessage.NOT_OWNER, SessionStatusCode.NOT_OWNER)
        if session_data.end_time:
            await self._check_dif_date(session.start_time , session_data.end_time)

        updated_session = await self.session_repository.update_session(session_id, session_data.model_dump(exclude_unset=True))

        logger.info('session update success with data: %s',updated_session)
        response = SessionResponse.model_validate(updated_session)
        await self._handle_response(response)
        return ResponseModel(data=response)
    async def delete_session(self, session_id:str):
        await self.session_repository.delete_session(session_id)
        return ResponseModel()


    async def get_list_sessions(self, filters: FilterSessionModel)-> ResponsePaginatedModel:
        list_sessions, total = await self.session_repository.get_list_session(filters)

        list_sessions_response = []
        for session in list_sessions:
            response = SessionResponse.model_validate(session)
            await self._handle_response(response)
            list_sessions_response.append(response)
        return ResponsePaginatedModel(data=list_sessions_response, total=total, offset= filters.offset)

    async def get_session(self, session_id:str):
        session = await self.session_repository.get_session_by_id(session_id)
        if not session:
            raise SessionException(SessionMessage.NOT_FOUND, SessionStatusCode.NOT_FOUND)
        response = SessionResponse.model_validate(session)
        await self._handle_response(response)
        return ResponseModel(data=response)

    async def _handle_response(self, response:SessionResponse):
        logger.info(f'response {response}')
        filter_task = FilterWorkItemModel(limit=10, offset=0,list_ids=response.list_task)
        logger.info(f'filter_task: {filter_task}')
        list_tasks = await self.work_item_repository.filter_work_item_for_order(filter_task)
        list_task_res = []
        # logger.info(f'list_tasks: {list_tasks}')
        for task in list_tasks:
            # count subtask done/ total =process_percent
            filter_subtask_done = FilterWorkItemModel(status=[TaskStatusEnum.DONE], parent=str(task.id), offset=0, limit=1)
            count_sub_task_done = await self.work_item_repository.count_work_item(filter_subtask_done)

            filter_all_subtask = FilterWorkItemModel(status=[TaskStatusEnum.NEW, TaskStatusEnum.PROCESSING], parent=str(task.id), offset=0, limit=1)
            count_total_subtask = await self.work_item_repository.count_work_item(filter_all_subtask) + count_sub_task_done
            task_response = TaskResponse.model_validate(task)

            task_response.percent_process = count_sub_task_done/count_total_subtask if count_total_subtask else 0
            list_task_res.append(task_response)
        response.list_tasks_data = list_task_res

    async def checkout(self, user_id: str, session_id:str, session_data: CheckoutModel, background_tasks: BackgroundTasks) -> ResponseModel:
        session = await self.check_user_checkout(user_id, session_id)
        # update session
        update_session_data = UpdateSessionModel(**session_data.model_dump(exclude_unset=True), status=SessionStatusEnum.DONE)
        if not update_session_data.end_time:
            update_session_data.end_time = datetime.now()
        logger.info('session : %s', session)
        logger.info('session update success with data: %s', update_session_data)
        # check case end_time has diff date with start time
        await self._check_dif_date(session.start_time ,update_session_data.end_time)

        # background job handle update
        await self._handle_update_status_task_done(session_data, session_id)

        data_dump = update_session_data.model_dump(exclude_unset=True)
        updated_session = await self.session_repository.update_session(session_id, data_dump)
        if not updated_session:
            raise SessionException(SessionMessage.NOT_FOUND, SessionStatusCode.NOT_FOUND)
        response = SessionResponse.model_validate(updated_session)

        # inject call webhook
        # get token
        departments = [f"DEPARTMENT_{department}" for department in
                       response.user.department] if response.user.department else []
        filter_chat_token = FilterChatbotTokenModel(offset=0, limit=100, position=departments, type=[ChatbotTypeEnum.DEFAULT])
        # print("filter_chat_token : ",filter_chat_token)
        filter_chat_token_master = FilterChatbotTokenModel(offset=0, limit=1, type=[ChatbotTypeEnum.MASTER.value])

        chat_token, total = await self.chatbot_token_repository.get_list_chatbot_tokens(filter_chat_token)
        token_master, total_master = await self.chatbot_token_repository.get_list_chatbot_tokens(
            filter_chat_token_master)

        chat_token.extend(token_master)
        print("chat token", chat_token)
        if total + total_master > 0:
            list_subtasks = [ subtask.id for subtask in session_data.list_subtasks]
            list_task_data = await self._handle_subtask_form_checkout(list_subtasks)
            if not list_task_data:
                filters_task = FilterWorkItemModel(offset=0, limit=len(session.list_task), list_ids=session.list_task)
                list_subtasks, total = await self.work_item_repository.get_list_work_items(filters_task)
            # await asyncio.gather(*[
            #     self.get_work_item_by_id(work_id.id, list_task, list_task_data)
            #     for work_id in session_data.list_subtasks
            # ])
            departments = None
            if response.user and response.user.department:
                filter_depart = FilterDepartmentModel(offset=0, limit=len(response.user.department), list_ids=response.user.department)
                departments, total = await self.department_repository.get_list_departments(filter_depart)
                if total:
                    departments = [department.name for department in departments]
                else:
                    departments = None
            content = FormatContentGgChatAPI.format_content_checkout(response.user.name, list_task_data, session_data.note_result, departments, session_data.end_time, response.user.nickname, session_data.checkout_late, session_data.departure_status, response.work_form, response.evaluate_session)
            for token in chat_token:
                GgChatWebhookUtil.call_webhook(content, token.space_id, token.key, token.token)
            response.list_tasks_data = list_task_data
        return ResponseModel(data=response)

    async def _handle_update_task(self, item: UpdateSubTaskModel, session_id:str, list_task_id: set[str]):
        work_item = await self.work_item_repository.get_work_item_by_id(item.id)
        if not work_item:
            raise TaskException(TaskMessage.SUBTASK_NOT_FOUND, TaskStatusCode.SUBTASK_NOT_FOUND)

        if work_item.type not in [WorkItemType.TASK.value, WorkItemType.SUBTASK.value]:
            raise SessionException(SessionMessage.TASK_SUBTASK_TYPE_NOT_MATCH,
                                   SessionStatusCode.TASK_SUBTASK_TYPE_NOT_MATCH)
        logger.info ('subtask : %s', work_item)
        if work_item.type == WorkItemType.SUBTASK.value:
            if item.status == TaskStatusEnum.DONE.value:
                update_data = UpdateTaskModel(status=item.status, session_id=session_id)
            else:
                update_data = UpdateTaskModel(status=item.status,session_id=None)
            updated_subtask = await self.work_item_repository.update_work_item(item.id, update_data.model_dump(exclude_unset=True))
            if updated_subtask and updated_subtask.parent and updated_subtask.status == TaskStatusEnum.DONE:
                list_task_id.add(str(updated_subtask.parent))
            # update task to be process if change subtask status
            elif updated_subtask and updated_subtask.parent and updated_subtask.status != TaskStatusEnum.DONE:
                task = await self.work_item_repository.get_work_item_by_id(updated_subtask.parent)
                if task and task.status == TaskStatusEnum.DONE:
                    update_task_data = UpdateTaskModel(status=TaskStatusEnum.PROCESSING, session_id=None)
                    await self.work_item_repository.update_work_item(str(task.id), update_task_data.model_dump(exclude_unset=True))

    async def get_work_item_by_id(self, work_item_id:str, list_title: list, list_data: list):
        work_item = await self.work_item_repository.get_work_item_by_id(work_item_id)
        if work_item:
            list_title.append(work_item.title)
            list_data.append(TaskResponse.model_validate(work_item))

    async def _handle_subtask_form_checkout(self, list_subtask: list):
        parent_map = dict()
        list_subtask_filter = FilterWorkItemModel(list_ids=list_subtask, offset=0, limit=len(list_subtask))
        list_subtask_data, total = await self.work_item_repository.get_list_work_items(list_subtask_filter)

        for subtask in list_subtask_data:
            parent_id = subtask.parent
            if parent_id not in parent_map:
                parent_obj = TaskResponse.model_validate(subtask.parent_model)
                parent_obj.children = []
                parent_map[parent_id] = parent_obj
                logging.info(" case subtask of story: %s", subtask)

            parent_map[parent_id].children.append(TaskResponse.model_validate(subtask))

        all_parents = list(parent_map.values())
        for parent in all_parents:
            all_subtasks = await self.work_item_repository.get_children(str(parent.id), status=[ status for status in TaskStatusEnum if status != TaskStatusEnum.CANCELED])
            parent.total_subtask = len(all_subtasks)
            count_subtask_done = 0
            for subtask in parent.children:
                if subtask.status == TaskStatusEnum.DONE:
                    count_subtask_done += 1
            parent.estimated_point = math.floor(count_subtask_done / len(all_subtasks) * parent.point + 0.5) if count_subtask_done else 0
        return all_parents

    async def remind_checkin(self):
        # get list session -> list user_id distinct checkin today
        # get list user not in list user_id
        # call api to remind
        start_of_today_vn = DateTimeUtil.get_start_time_today()
        logger.info(f"start_of_today_vn: %s{start_of_today_vn}")
        filters = FilterCheckInSessionModel(start_time=start_of_today_vn)
        list_user_id = await self.session_repository.get_all_sessions_checkin(filters)
        logger.info(f"list_user_id: %s{list_user_id}")

        list_user_not_checkin = await self.user_repository.get_all_user_not_match_id(list_user_id)

        logger.info(f"list_user_not_checkin: %s{list_user_not_checkin}")
        filter_chat_token = FilterChatbotTokenModel(offset=0, limit=1)
        chat_token, total = await self.chatbot_token_repository.get_list_chatbot_tokens(filter_chat_token)
        for user in list_user_not_checkin:
            if total > 0 and UserRole.TASKER in user.roles and user.daily_checkin:
                content = FormatContentGgChatAPI.format_content_remind_checkin(user.name)
                GgChatWebhookUtil.call_webhook(content, chat_token[0].space_id, chat_token[0].key, chat_token[0].token)
        return

    async def remind_checkout(self):
        # get list session with end_time = None in today
        start_of_today_vn = DateTimeUtil.get_start_time_today()
        logger.info(f"start_of_today_vn: %s{start_of_today_vn}")

        filters = FilterCheckInSessionModel(start_time=start_of_today_vn, status=[SessionStatusEnum.NEW, SessionStatusEnum.IN_PROGRESS])

        list_user_id = await self.session_repository.get_all_sessions_checkin(filters)
        logger.info(f"list_user_id: %s{list_user_id}")

        list_user_name = await self.user_repository.get_all_user_match_id(list_user_id)
        filter_chat_token = FilterChatbotTokenModel(offset=0, limit=1)
        chat_token, total = await self.chatbot_token_repository.get_list_chatbot_tokens(filter_chat_token)
        for user in list_user_name:
            if total > 0:
                content = FormatContentGgChatAPI.format_content_remind_checkout(user.name)
                GgChatWebhookUtil.call_webhook(content, chat_token[0].space_id, chat_token[0].key, chat_token[0].token)
        return

    async def _check_dif_date(self,start_time: datetime|None, end_time: datetime|None ):
        local_tz = ZoneInfo(settings.TZ)
        local_start = start_time.astimezone(local_tz)
        local_end = end_time.astimezone(local_tz)

        if local_end and local_end <= local_start:
            raise SessionException(SessionMessage.START_GTE_END_TIME, SessionStatusCode.START_GTE_END_TIME)
        if start_time and end_time:
            logger.info(f"start_time: %s{start_time}")
            logger.info(f"end_time: %s{end_time}")

            logger.info(f"local_start: %s{local_start}")
            logger.info(f"local_end: %s{local_end}")
            if local_end.date() != local_start.date():
                raise SessionException(SessionMessage.CHECKOUT_DIFF_DATE, SessionStatusCode.CHECKOUT_DIFF_DATE)
        else:
            raise SessionException(SessionMessage.CHECKOUT_DIFF_DATE, SessionStatusCode.CHECKOUT_DIFF_DATE)

    async def get_session_by_date_range(self, filters: FilterSessionByDateRangeModel):
        list_date_session = await self.session_repository.get_session_by_date_range(filters)
        # handle add task, subtask to each session
        # cal point estimate, % process
        # iterate over date -> sessions ->list subtask in session
        list_session = []
        for index, date_session in enumerate(list_date_session):
            list_session_w_task_data = []
            for session in date_session.sessions:
                # get subtask by session_id -> group by parent
                # % process
                list_task_data = await self.calc_process_task_session(str(session.id))
                session_response = SessionTaskResponse.model_validate(session.model_dump())
                session_response.list_tasks_data = list_task_data
                list_session_w_task_data.append(session_response)

            date_session.sessions = list_session_w_task_data
            print(date_session.sessions)
            list_session.append(date_session)

        # print("test",list_session)

        return ResponsePaginatedModel(data=list_session, total=len(list_date_session), offset=0)

    async def _handle_update_status_task_done(self, session_data: CheckoutModel, session_id: str):
        list_task_id= set()
        # logger.debug(f"list_task_id: %s{session_data.list_subtasks}")

        for item in session_data.list_subtasks:
            await self._handle_update_task(item, session_id, list_task_id)

        for task in list_task_id:
            # count subtask done/ total =process_percent
            filter_subtask_done = FilterWorkItemModel(status=[TaskStatusEnum.DONE], parent=str(task), offset=0, limit=1)
            count_sub_task_done = await self.work_item_repository.count_work_item(filter_subtask_done)

            filter_all_subtask = FilterWorkItemModel(status=[TaskStatusEnum.NEW, TaskStatusEnum.PROCESSING], parent=str(task), offset=0, limit=1)
            count_total_subtask = await self.work_item_repository.count_work_item(filter_all_subtask) + count_sub_task_done
            logger.info(f"count_sub_task_done: %s{count_sub_task_done}")
            logger.info(f"count_total_subtask: %s{count_total_subtask}")
            if  count_total_subtask == count_sub_task_done and count_sub_task_done > 0:
                update_data = UpdateTaskModel(status=TaskStatusEnum.DONE, session_id=session_id)
                await self.work_item_repository.update_work_item(task, update_data.model_dump(
                    exclude_unset=True))
            # else:
            #     update_data = UpdateTaskModel(status=TaskStatusEnum.PROCESSING)
            #     await self.work_item_repository.update_work_item(task, update_data.model_dump(
            #         exclude_unset=True))

    async def calc_process_task_session(self, session_id: str):
        parent_map = dict()
        list_task = []

        subtask_done_map = dict()
        filter_subtask = FilterWorkItemModel(type= [WorkItemType.SUBTASK],session_id=str(session_id), limit=10, offset=0)
        list_subtask = await self.work_item_repository.filter_work_item_for_order(filter_subtask)
        for subtask in list_subtask:
            task_id = subtask.parent
            if task_id not in parent_map:
                task_obj = TaskResponse.model_validate(subtask.parent_model)
                task_obj.children = []
                parent_map[task_id] = task_obj
                subtask_done_map[task_id] = 1 if subtask.status == TaskStatusEnum.DONE else 0
            else:
                if subtask.status == TaskStatusEnum.DONE:
                    subtask_done_map[task_id] +=1
            parent_map[task_id].children.append(TaskResponse.model_validate(subtask))

        for key, value in parent_map.items():
            all_subtasks = await self.work_item_repository.get_children(key, status=[ status for status in TaskStatusEnum if status != TaskStatusEnum.CANCELED])
            # print("all_subtasks:", len(all_subtasks))
            # print("done subtasks:", subtask_done_map[key])
            percent_process = subtask_done_map[key]/len(all_subtasks) if len(all_subtasks) > 0 else 0
            parent_map[key].percent_process = percent_process
            # print("percent_process:", parent_map[key].percent_process)
            parent_map[key].estimated_point = math.floor(percent_process * parent_map[key].point + 0.5)
            # print("check task",parent_map[key].estimated_point)
            parent_map[key].total_subtask = len(all_subtasks)

        list_task[:] = list(parent_map.values())
        return list_task

    async def check_user_checkin(self, user_id:str):
        filters_in_session = FilterCheckInSessionModel(start_time=DateTimeUtil.get_start_time_today(),
                                                       status=[SessionStatusEnum.NEW, SessionStatusEnum.IN_PROGRESS])
        list_user_checkin = await self.session_repository.get_all_sessions_checkin(filters_in_session)
        logger.info('session today: %s', list_user_checkin)
        if list_user_checkin:
            if user_id in list_user_checkin:
                raise SessionException(SessionMessage.SESSION_CHECKED_IN, SessionStatusCode.SESSION_CHECKED_IN)

    async def check_user_checkout(self, user_id:str, session_id:str):
        session = await self.session_repository.get_session_by_id(session_id)
        if not session:
            raise SessionException(SessionMessage.NOT_FOUND, SessionStatusCode.NOT_FOUND)

        if session.status == SessionStatusEnum.DONE:
            raise SessionException(SessionMessage.USER_CHECKED_OUT, SessionStatusCode.USER_CHECKED_OUT)
        # update work item: task, subtask,
        # add session_id in to subtask
        # if user_id != session.user_id:
        #     raise SessionException(SessionMessage.NOT_OWNER, SessionStatusCode.NOT_OWNER)
        return session

    async def checkin_comgao(self, data: CreateSessionComgao):
        # input : list email
        # url to send noti
        # check user in session
        #
        logger.info('session comgao: %s', data)
        list_session = []
        user_ids = []
        map_user_session = {}
        for email in data.emails:
            user = await self.user_repository.get_user_by_email(email)
            if not user:
                raise ExceptionUserNotFound()
            create_session = CreateSessionModel(
                user_id=str(user.id), status=SessionStatusEnum.NEW,
                list_task =[], start_time=data.start_time, notes= data.notes, work_form=data.work_form, checkin_late=data.checkin_late, arrival_status=data.arrival_status
            )
            list_session.append(create_session)
            user_ids.append(str(user.id))
        await asyncio.gather(*(
            self.check_user_checkin(user_id) for user_id in user_ids
            ),return_exceptions=False
        )
            # check in session
        results = await asyncio.gather(
            *(self.create_session(session) for session in list_session),
            return_exceptions=False
        )
        # list_session_res = []
        for result in results:
            map_user_session[str(result.data.id)] = result.data.user_id
            # list_session_res.append(str(result.data.id))

        return ResponseModel(data=map_user_session)

    async def checkout_comgao(self, data: CheckoutComgaoModel, background_tasks: BackgroundTasks):
        await asyncio.gather(*(
            self.check_user_checkout(value, key)
            for key, value in data.map_user_session.items()
            ), return_exceptions=False
        )
        data_checkout = CheckoutModel(**data.model_dump())
        results = await asyncio.gather(
            *(self.checkout(value,key, data_checkout, background_tasks)
              for key, value in data.map_user_session.items()
              ),
            return_exceptions=False
        )
        list_response = []
        for result in results:
            list_response.append(result.data)
        return ResponsePaginatedModel(data=list_response, total=len(list_response), offset=0)