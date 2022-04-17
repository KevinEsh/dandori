query_materials = '''
query {
  materials(orderBy: { desc: ID }) {
    id
    name
    insertedAt
    updatedAt
  }
}
'''
query_resources_validator = '''
query {
  resources(orderBy: { desc: ID }) {
    id
    name
    insertedAt
    updatedAt
    resourceType
    resourceMaterials {
      id
      material {id}
    }
  }
}
'''

query_inventory_validator = '''
query Lots{
  inventoryGroups(limit: 2, orderBy: { desc: ID }) {
    id
    insertedAt
    updatedAt
    lots {
      startAt
      endAt
      id
      insertedAt
      material{ id }
      quantity
      resource{ id }
      updatedAt
    }
  }
}
'''

query_orders_validator = '''
query order{
  orders(filter:{demandId:"%s"}) {
    code
    demand{ id }
    endAt
    id
    insertedAt
    material{ id }
    priority
    startAt
    updatedAt
  }
}
'''

query_programs = '''
query Programs{
  programs {
    programEndTime:endAt
    programID:id
    inventoryGroupId
    programStart: startAt
    toSolveId
    status
  }
}
'''

query_stops = '''
# Write your query or mutation here
query order{
  stops  {
    id
    endAt
    resources {
      id
    }
    startAt
  }
}
'''

query_orders = '''
query order{
  orders(filter:{demandId:"%s"}) {
    code
    demandId
    OrderEnd:endAt
    OrderID:id
    OrderRequestTime:insertedAt
    materialId
    priority
    OrderStart:startAt
    OrderUpdateTime:updatedAt
  }
}
''' 

query_materials = '''
query {
  materials(orderBy: { desc: ID }) {
    matid:id
    name
    materialInsertedTime:insertedAt
    materialUpdatetTime:updatedAt
  }
}
'''
query_resources = '''
query {
  resources(orderBy: { desc: ID }) {
    resourceId:id
    resourceName:name
    ResourceInsertedTime:insertedAt
    ResourceUpdateTime:updatedAt
    resourceType
    resourceMaterials {
      matid:id
      materialId
    }
  }
}
'''

query_inventory = '''
query Lots{
  inventoryGroups(limit: 2, orderBy: { desc: ID }) {
    id
    insertedAt
    updatedAt
    lots {
      lotStartTime:startAt
      lotEndTime:endAt
      lotID:id
      lotInsertTime:insertedAt
      materialId
      matQuant:quantity
      resourceId
      lotUpdate:updatedAt
    }
  }
}
'''
