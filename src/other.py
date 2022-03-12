from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['passwords'] = []
    store['channels'] = []
    store['no_users'] = True
    data_store.set(store)
    return {
    }