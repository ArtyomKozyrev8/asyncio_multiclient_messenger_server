"""
To create server side of the application module asyncio was used. Please see High Level API DOCS the Stream part.
"""


import asyncio
from asyncio import StreamReader, StreamWriter, TimeoutError
from queue import Queue  # I decided to use Queue since it is FIFO structure

# address_storage is used instead of database
# key is a client_name to whom message should be sent
# value is a Queue which stores message which should be sent to the client
address_storage = {}


async def reader_cycle(reader_: StreamReader, client_name: str):
    """
    The function listens to incoming messages from the concrete client.
    Then the message is put to the Queue of receiver in address_storage
    :param reader_: stream receives incoming messages from the client
    :param client_name: the name of the client we receive message in the stream from
    :return: None
    """
    while True:
        try:
            message = await asyncio.wait_for(reader_.read(100), timeout=0.5)  # wait 0.5 seconds for incoming message
        except TimeoutError:
            pass  # otherwise raise error to retunr control to writer Task
        else:
            if message:
                message = message.decode('utf8')
                result = message.split("***")
                if len(result) == 2:  # check if incoming message have correct format
                    to_whom, words = result
                    # build message to send to Queue of receiver
                    # '|' is used to separate messages from each other, since several senders can send message
                    # to one clients simultaneously and client need some mechanism to separate these messages
                    # from one another.
                    mes = f"{client_name}***{words}|"
                    # client_name is the name of sender in the case
                    if to_whom in address_storage.keys():
                        address_storage[to_whom].put(mes)


async def writer_cycle(writer_: StreamWriter, client_name: str):
    """
    The function check if there are any messages in the incoming Queue for the client,
    then take one message and send it to the stream with the client
    :param writer_: stream with the receiver client
    :param client_name: name of the receiver client
    :return: None
    """
    while True:
        if not address_storage[client_name].empty():
            message = address_storage[client_name].get()
            writer_.write(message.encode('utf8'))
            await writer_.drain()

        await asyncio.sleep(0.5)  # return control to another Task/Corouitine


async def incoming_call_handler(reader: StreamReader, writer: StreamWriter):
    """
    Check Asyncio Stream High Level API Documentation
    :param reader: stream for incoming messages for client
    :param writer: stream for outcomming messages to the client
    :return:
    """
    try:
        client_ip = writer.get_extra_info('peername')  # get ip address of client host
        client_name = await reader.read(100)  # get alias of the client
        if client_name:
            client_name = client_name.decode('utf8')
            print(f"Incomming connection from: ip {client_ip}, name: {client_name}")

            # create (if not exits) Queue for incomming messages for the client
            if client_name not in address_storage:
                address_storage[client_name] = Queue()
    except ConnectionResetError as ex:
        print(f"Failed to establish connection with client: {ex}")
    else:
        # create Two Tasks (see asyncio docs) explicitly
        # otherwise you can use asyncio.gather to create Tasks
        # Tasks run "simultaneously"
        read_task = asyncio.create_task(reader_cycle(reader, client_name))
        write_task = asyncio.create_task(writer_cycle(writer, client_name))

        try:
            await read_task
            await write_task
        except ConnectionResetError as ex:
            print(f"Connection with ip {client_ip}, name: {client_name} was finished due to error: {ex}")


async def main():
    # please check documentation how to create asyncio stream server
    server = await asyncio.start_server(incoming_call_handler, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    # start server
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
