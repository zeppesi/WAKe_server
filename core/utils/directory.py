import os


def find_dynamic_route(file_name):
    """
    file_name을 project 기준으로 적어주시면 좋습니다.
    즉 manage.py를 찾는다고 할 때,
    manage.py가 아닌 Wake_server/manage.py으로 적어주시는게 좋습니다.
    """

    current_directory = os.getcwd()
    # 최상위 디렉토리까지 올라가면서 file_name 찾기
    while current_directory != '/':
        json_file = os.path.join(current_directory, file_name)
        if os.path.isfile(json_file):
            break

        # 상위 디렉토리로 이동
        current_directory = os.path.dirname(current_directory)
    else:
        raise Exception("가장 가까운 파일을 찾을 수 없습니다.")
    return json_file
